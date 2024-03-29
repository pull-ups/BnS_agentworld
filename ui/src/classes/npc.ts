import { Actor } from "./actor";
import { Player } from "./player";
import { DIRECTION } from "../utils";
import {
  MoveTo,
  PathFinder,
  Board,
} from "../phaser3-rex-plugins/plugins/board-components";
import { Label, TextArea } from "../phaser3-rex-plugins/templates/ui/ui-components";
import { COLOR_DARK, COLOR_LIGHT, COLOR_PRIMARY } from "../constants";
import { TownScene } from "../scenes";

import eventsCenter from "./event_center";

export class NPC extends Actor {
  private moveTo: MoveTo;
  private board: Board;
  private canMove: boolean = true;
  private talkWithPlayer: boolean = false;
  private doingtask: boolean = false;     // doing 뻘짓
  private doingreaction: boolean = false; // doing reaction
  private dialoghistory: string[] = [];   //대화 기록
  private dialoghistory_string: string = "";  //대화 기록
  private curtaskendtime: number = 0;
  private path: PathFinder.NodeType[] = [];
  private finalDirection: number = undefined;
  private targetLocation: string = undefined;
  private targetNPC: NPC = undefined;
  private textBox: Label = undefined;
  private chatBox: Label = undefined;   //대화 보여주는 창 객체
  private nameBox: Label = undefined;
  private reaction: string = ""; //현재 situation에 대한 reaction 내용
  private reaction_plan: string[] = []; //reaction에 대한 plan

  public id: number;
  public direction: number = DIRECTION.DOWN;

  constructor(
    scene: Phaser.Scene,
    board: Board,
    x: number,
    y: number,
    name: string,
    id: number
  ) {
    super(scene, x, y, name);

    this.setName(name);
    this.board = board;
    this.id = id;
    // PHYSICS
    this.getBody().setSize(14, 16);
    this.getBody().setOffset(0, 4);
    this.getBody().setImmovable(true);
    this.setOrigin(0, 0.2);

    this.initAnimations();
    this.moveTo = this.scene.rexBoard.add.moveTo(this, {
      speed: 55,
      sneak: true,
    });
    this.listenToDirectionEvent();
  }

  update(): void {
    if (this.path.length > 0 && !this.moveTo.isRunning && this.canMove) {
      var tileXY = this.board.worldXYToTileXY(this.x, this.y);
      if (tileXY.x == this.path[0].x) {
        if (tileXY.y < this.path[0].y) this.changeDirection(DIRECTION.DOWN);
        else if (tileXY.y > this.path[0].y) this.changeDirection(DIRECTION.UP);
      } else if (tileXY.y == this.path[0].y) {
        if (tileXY.x < this.path[0].x) this.changeDirection(DIRECTION.RIGHT);
        else if (tileXY.x > this.path[0].x)
          this.changeDirection(DIRECTION.LEFT);
      }
      var move = this.moveTo.moveTo(this.path.shift());
      move.removeAllListeners("complete");
      move.on("complete", () => {
        if (this.path.length == 0) {
          this.changeDirection(this.finalDirection);
          this.emitTurnEvent();
          if (this.targetLocation != undefined) {
            fetch("http://127.0.0.1:10003/update_location", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              credentials: "same-origin",
              body: JSON.stringify({
                agent_locations: {
                  [this.name]: this.targetLocation,
                },
              }),
            });
          }
        }
      });
    }

    var text = "";
    switch (this.direction) {
      case DIRECTION.UP:
        text = "up";
        break;
      case DIRECTION.DOWN:
        text = "down";
        break;
      case DIRECTION.LEFT:
        text = "left";
        break;
      case DIRECTION.RIGHT:
        text = "right";
        break;
    }
    this.anims.play(this.name + "-walk-" + text, true);
    if (this.anims.isPlaying && !this.moveTo.isRunning)
      this.anims.setCurrentFrame(this.anims.currentAnim!.frames[0]);
    this.updateTextBox();
    this.updateChatBox();
    this.depth = this.y + this.height * 0.8;
  }

  listenToDirectionEvent(): void {
    eventsCenter.on(this.name + "-up", () => {
      this.changeDirection(DIRECTION.UP);
    });
    eventsCenter.on(this.name + "-down", () => {
      this.changeDirection(DIRECTION.DOWN);
    });
    eventsCenter.on(this.name + "-left", () => {
      this.changeDirection(DIRECTION.LEFT);
    });
    eventsCenter.on(this.name + "-right", () => {
      this.changeDirection(DIRECTION.RIGHT);
    });
  }

  emitTurnEvent(): void {
    // Make the listener NPC turn to the speaker NPC.
    if (this.targetNPC == undefined) return;
    var direction = "";
    switch (this.finalDirection) {
      case DIRECTION.UP:
        direction = "down";
        break;
      case DIRECTION.DOWN:
        direction = "up";
        break;
      case DIRECTION.LEFT:
        direction = "right";
        break;
      case DIRECTION.RIGHT:
        direction = "left";
        break;
    }
    eventsCenter.emit(this.targetNPC.name + "-" + direction);
    this.setTargetNPC();
  }

  updateTextBox(): void {
    if (this.textBox == undefined) return;
    this.textBox.setOrigin(0.5, 1.0);
    var scale = this.scene.cameras.main.zoom;
    this.textBox.setX(this.x + this.width / 2);
    this.textBox.setY(this.y - this.height * 0.2);
    this.textBox.depth = this.y + this.height * 0.8;
    this.textBox.getChildren().forEach((child) => {
      child.setDepth(this.y + this.height * 0.8);
    });
  }
  updateChatBox(): void {
    if (this.chatBox == undefined) return;
   
  }
  // nameBox
  public setNameBox(): void {
    this.destroyNameBox();

    const mapping = {
      "Jinsoyun": "진서연",
      "Yura": "유란",
      "HongSokyun": "홍석근",
      "Lusung": "무성"
    };
  
    var scale = this.scene.cameras.main.zoom;
    var scene = this.scene as TownScene;
    this.nameBox = scene.rexUI.add
      .label({
        x: this.x + this.width / 2,
        //y: this.y - this.height * 0.2,
        y: this.y + 20,
        width: 25 * scale,
        orientation: "x",
        background: scene.rexUI.add.roundRectangle(
          0,
          0,
          2,
          2,
          20,
          COLOR_PRIMARY,
          0.7
        ),
        text: scene.rexUI.wrapExpandText(
          scene.add.text(0, 0, mapping[this.name], {
            fontSize: 20,
            align: "center",
          })
        ),
        expandTextWidth: true,
        space: {
          left: 10,
          right: 10,
          top: 10,
          bottom: 10,
        },
      })
      .setOrigin(0.5, 0.0)
      .setScale(1 / scale, 1 / scale)
      .setDepth(this.y + this.height * 0.8)
      .layout();
  }

  public destroyNameBox(): void {
    if (this.nameBox != undefined) this.nameBox.destroy();
    this.nameBox = undefined;
  }

  public setReactionBox(text_short: string, text_long: string, player: Player): void {
    this.destroyTextBox();
    var scale = this.scene.cameras.main.zoom;
    var scene = this.scene as TownScene;
    
    this.textBox = scene.rexUI.add
      .label({
        x: this.x + this.width / 2,
        y: this.y - this.height * 0.2,
        width: 48 * scale,
        orientation: "x",
        background: scene.rexUI.add.roundRectangle(
          0,
          0,
          2,
          2,
          20,
          COLOR_PRIMARY,
          0.7
        ),
        text: scene.rexUI.wrapExpandText(
          scene.add.text(0, 0, text_short, {
            fontSize: 15,
          })
        ),
        expandTextWidth: true,
        space: {
          left: 10,
          right: 10,
          top: 10,
          bottom: 10,
        },
      })
      .setOrigin(0.5, 1.0)
      .setScale(1 / scale, 1 / scale)
      .setDepth(this.y + this.height * 0.8)
      .layout();
    this.textBox.setInteractive();

    // Register the click event handler
    this.textBox.on('pointerdown', () => this.setPlanbox(text_long, player));
  }

  private setPlanbox(text_long: string, player: Player): void {
    var plan="1. A, 2. B, 3. C";
    var scale = this.scene.cameras.main.zoom;
    var scene = this.scene as TownScene;
    var camera_height = this.scene.cameras.main.height;
    this.chatBox = scene.rexUI.add
      .label({
        x: player.x + this.width / 2,
        y: player.y - this.height * 0.6 + camera_height * 0.1,
        width: 48 * scale * 6,
        height: 48 * scale * 3,
        orientation: "x",
        background: scene.rexUI.add.roundRectangle(
          0,
          0,
          2,
          2,
          20,
          COLOR_DARK,
          1
        ),
        text: scene.rexUI.wrapExpandText(
          scene.add.text(0, 0, text_long + "\n\n\n\n" + plan, {
            fontSize: 20,
          })
        ),
        expandTextWidth: true,
        space: {
          left: 10,
          right: 10,
          top: 10,
          bottom: 10,
        },
      })
      .setOrigin(0.5, 1.0)
      .setScale(1 / scale, 1 / scale)
      .setDepth(9999)
      .layout();

    var submitBtn = scene.rexUI.add
    .label({
      x: player.x,
      y: player.y+70,
      background: scene.rexUI.add
        .roundRectangle(0, 0, 2, 2, 20, COLOR_LIGHT)
        .setStrokeStyle(2, COLOR_LIGHT),
      text: scene.add.text(0, 0, "Close"),
      space: {
        left: 10,
        right: 10,
        top: 10,
        bottom: 10,
      },
      })
      .setOrigin(0)
      .setScale(1 / scale, 1 / scale)
      .setDepth(10000)
      .layout();
    submitBtn.setInteractive();
    submitBtn.on('pointerdown', () => {
      submitBtn.destroy();
      this.destroyChatBox()
    });


  }



  public setTextBox(text: string, player: Player, speaking: boolean = true): void {
    this.destroyTextBox();
    var scale = this.scene.cameras.main.zoom;
    var scene = this.scene as TownScene;
    var labelWidth = speaking ? 72 * scale : 40 * scale;
    this.textBox = scene.rexUI.add
      .label({
        x: this.x + this.width / 2,
        y: this.y - this.height * 0.2,
        width: labelWidth,
        orientation: "x",
        background: scene.rexUI.add.roundRectangle(
          0,
          0,
          2,
          2,
          20,
          COLOR_PRIMARY,
          0.7
        ),
        text: scene.rexUI.wrapExpandText(
          scene.add.text(0, 0, text, {
            fontSize: 15,
          })
        ),
        expandTextWidth: true,
        space: {
          left: 10,
          right: 10,
          top: 10,
          bottom: 10,
        },
      })
      .setOrigin(0.5, 1.0)
      .setScale(1 / scale, 1 / scale)
      .setDepth(this.y + this.height * 0.8)
      .layout();
    this.textBox.setInteractive();

    // Register the click event handler
    this.textBox.on('pointerdown', () => this.setChatbox(player));
  }

  private setChatbox(player: Player): void {
    var dialoghistory_string=this.getdialoghistorystring();
    var scale = this.scene.cameras.main.zoom;
    var scene = this.scene as TownScene;
    var camera_height = this.scene.cameras.main.height;
    this.chatBox = scene.rexUI.add
      .label({
        x: player.x + this.width / 2,
        y: player.y - this.height * 0.6 + camera_height * 0.1,
        width: 48 * scale * 6,
        height: 48 * scale * 5,
        orientation: "x",
        background: scene.rexUI.add.roundRectangle(
          0,
          0,
          2,
          2,
          20,
          COLOR_DARK,
          1
        ),
        text: scene.rexUI.wrapExpandText(
          scene.add.text(0, 0, dialoghistory_string, {
            fontSize: 20,
          })
        ),
        expandTextWidth: true,
        space: {
          left: 10,
          right: 10,
          top: 10,
          bottom: 10,
        },
      })
      .setOrigin(0.5, 1.0)
      .setScale(1 / scale, 1 / scale)
      .setDepth(9999)
      .layout();

    var submitBtn = scene.rexUI.add
    .label({
      x: player.x,
      y: player.y+70,
      background: scene.rexUI.add
        .roundRectangle(0, 0, 2, 2, 20, COLOR_LIGHT)
        .setStrokeStyle(2, COLOR_LIGHT),
      text: scene.add.text(0, 0, "Close"),
      space: {
        left: 10,
        right: 10,
        top: 10,
        bottom: 10,
      },
      })
      .setOrigin(0)
      .setScale(1 / scale, 1 / scale)
      .setDepth(10000)
      .layout();
    submitBtn.setInteractive();
    submitBtn.on('pointerdown', () => {
      submitBtn.destroy();
      this.destroyChatBox()
    });


  }
  public destroyTextBox(): void {
    if (this.textBox != undefined) this.textBox.destroy();
    this.textBox = undefined;
  }
  public destroyChatBox(): void {
    if (this.chatBox != undefined) {
      this.chatBox.destroy();
    }
    this.chatBox = undefined;
    console.log("destroy chatbox");
  }

  public changeDirection(direction: number): void {
    if (direction == undefined) return;
    this.direction = direction;
  }

  public moveAlongPath(
    path: PathFinder.NodeType[],
    finalDirection: number = undefined,
    targetLocation: string = undefined
  ): void {
    if (path.length == 0) return;
    if (this.moveTo.isRunning) return;
    if (this.path.length > 0) return;
    this.path = path;
    this.finalDirection = finalDirection;
    this.targetLocation = targetLocation;
  }

  public pauseMoving(): void {
    this.moveTo.stop();
    this.canMove = false;
  }

  public resumeMoving(): void {
    this.moveTo.resume();
    this.canMove = true;
  }

  public isMoving(): boolean {
    return this.moveTo.isRunning || this.path.length > 0;
  }

  public isTalking(): boolean {
    return this.talkWithPlayer;
  }
  public isDoingtask(): boolean {
    return this.doingtask;
  }
  public isDoingReaction(): boolean {
    return this.doingreaction;
  }
  public setTalking(talking: boolean): void {
    this.talkWithPlayer = talking;
  }

  public setTargetNPC(targetNPC: NPC = undefined): void {
    this.targetNPC = targetNPC;
  }


  public setdoingtask(curtime: number): void {
    const temp=this.doingtask;
    this.doingtask = curtime < this.curtaskendtime;
    if (this.doingtask != temp){
      console.log(this.name + " is doing task: " + this.doingtask);
    }  
  }

  public setcurtaskendtime(curtaskendtime: number): void {
    this.curtaskendtime = curtaskendtime;
  }
  public adddialoghistory(dialog: string): void {
    this.dialoghistory.push(dialog);
    this.dialoghistory_string += dialog + "\n\n";
  }
  public getdialoghistory(): string[] {
    return this.dialoghistory;
  }
  public getdialoghistorystring(): string {
    return this.dialoghistory_string;
  }
  public setreaction(reaction: string): void {
    if (reaction==""){
      this.reaction="";
      this.doingreaction=false;
    }
    else{
      this.reaction = reaction;
      this.doingreaction=true;
    }
  }

  public setreactionplan(doingreaction: boolean, reactionplan: string): void {
    this.doingreaction=doingreaction;
    if (doingreaction==true){
      this.reaction_plan = reactionplan.split(',').map(item => item.trim().split('. ')[1]);
    }
    else{
      this.reaction_plan = [];
    }
  }
  public getreaction(): string {
    return this.reaction;
  }
  public getreactionplan(): string[] {
    return this.reaction_plan;
  }

  public emptydialoghistory(): void {
    this.dialoghistory = [];
    this.dialoghistory_string="";
  }

}
