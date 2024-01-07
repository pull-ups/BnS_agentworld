'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var commonjs = require('@rollup/plugin-commonjs');
var pluginNodeResolve = require('@rollup/plugin-node-resolve');
var replace = require('@rollup/plugin-replace');
var serve = require('rollup-plugin-serve');
var typescript = require('@rollup/plugin-typescript');

const path = require('path');

var rollup_config_dev = {

    //  Our game entry point (edit as required)
    input: [
        './src/index.ts'
    ],

    //  Where the build file is to be generated.
    //  Most games being built for distribution can use iife as the module type.
    //  You can also use 'umd' if you need to ingest your game into another system.
    //  If using Phaser 3.21 or **below**, add: `intro: 'var global = window;'` to the output object.
    output: {
        file: './dist/bundle.js',
        name: 'MyGame',
        format: 'iife',
        sourcemap: true
    },

    plugins: [

        //  Toggle the booleans here to enable / disable Phaser 3 features:
        replace({
            preventAssignment: true,
            'typeof CANVAS_RENDERER': JSON.stringify(true),
            'typeof WEBGL_RENDERER': JSON.stringify(true),
            'typeof WEBGL_DEBUG': JSON.stringify(true),
            'typeof EXPERIMENTAL': JSON.stringify(true),
            'typeof PLUGIN_CAMERA3D': JSON.stringify(false),
            'typeof PLUGIN_FBINSTANT': JSON.stringify(false),
            'typeof FEATURE_SOUND': JSON.stringify(true)
        }),

        //  Parse our .ts source files
        pluginNodeResolve.nodeResolve({
            browser: true,
            extensions: [ '.ts', '.tsx' ]
        }),

        //  We need to convert the Phaser 3 CJS modules into a format Rollup can use:
        commonjs({
            include: [
                'node_modules/eventemitter3/**',
                'node_modules/phaser/**'
            ],
            exclude: [ 
                'node_modules/phaser/src/polyfills/requestAnimationFrame.js',
                'node_modules/phaser/src/phaser-esm.js'
            ],
            sourceMap: true,
            ignoreGlobal: true
        }),

        //  See https://github.com/rollup/plugins/tree/master/packages/typescript for config options
        typescript(),

        //  See https://www.npmjs.com/package/rollup-plugin-serve for config options
        serve({
            open: true,
            contentBase: 'dist',
            host: '127.0.0.1',
            port: 10001,
            headers: {
                'Access-Control-Allow-Origin': '*'
            },
            
            historyApiFallback: false, // Add this line
            
            // setup: function(server) {
            //     server.get('/anotherpage', function (req, res) {
            //         const resolvedPath = path.resolve(__dirname, './dist/anotherpage.html');
            //         console.log('Serving:', resolvedPath);
            //         res.sendFile(resolvedPath);
            //     });
            // }
            setup: function(server) {
                server.get('/anotherpage', function (req, res) {
                    res.send('Another page is working');
                });
            }
        })

    ]
};

exports.default = rollup_config_dev;
