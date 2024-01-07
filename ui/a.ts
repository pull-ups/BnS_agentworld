  // private setChatbox(totaltext: string, player: Player): void {
    
  //   var scale = this.scene.cameras.main.zoom;
  //   var scene = this.scene as TownScene;
    
  //   var width = scene.cameras.main.width;
  //   var height = scene.cameras.main.height;
  //   var scale = scene.cameras.main.zoom;


  //   var background = scene.rexUI.add.roundRectangle(0, 0, width * 0.5, height * 0.5 , 0, COLOR_PRIMARY)
  //     .setOrigin(0) // Match origin with textarea
  //     .setPosition(player.x - 0.25 * width, player.y-0.25*height) // Position background relative to textarea
  //     // .setScale(1 / scale, 1 / scale); // Scale the background

  //   this.chatBox = scene.rexUI.add
  //   .textArea({
  //     x: player.x,
  //     y: player.y-20,
  //     width: width,
  //     height: height,
  //     // background: scene.rexUI.add.roundRectangle(0, 0, width, height, 0, COLOR_PRIMARY),
  //     background: background,
  //     text: scene.rexUI.add.BBCodeText(0, 0, totaltext), 
  //   })
  //   .setOrigin(0)
  //   .setScale(1 / scale, 1 / scale)
  //   .setAlpha(0.8);


  //   var submitBtn = scene.rexUI.add
  //   .label({
  //     x: 0,
  //     y: 0,
  //     background: scene.rexUI.add
  //       .roundRectangle(0, 0, 2, 2, 20, COLOR_PRIMARY)
  //       .setStrokeStyle(2, COLOR_LIGHT),
  //     text: scene.add.text(0, 0, "Close"),
  //     space: {
  //       left: 10,
  //       right: 10,
  //       top: 10,
  //       bottom: 10,
  //     },
  //     })
  //     .setOrigin(0)
  //     .setPosition(player.x-6, player.y+55)
  //     .setScale(1 / scale, 1 / scale)
  //     .layout();
    
    
    
  //   submitBtn.setInteractive();
  //   submitBtn.on('pointerdown', () => {
  //     submitBtn.destroy();
  //     this.destroyChatBox()
  //   });
  // }
