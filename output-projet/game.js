/**
 * @file game.js - Moteur de jeu Super Mario style 8-bit
 * @description Moteur de jeu complet avec physique, audio synthétisé et rendu pixel art.
 */

"use strict";

/**
 * CONFIGURATION ET CONSTANTES
 */
const CONFIG = {
    WIDTH: 256,
    HEIGHT: 240,
    SCALE: 3,
    FPS: 60,
    TILE_SIZE: 16,
    GRAVITY: 0.45,
    FRICTION: 0.8,
    JUMP_FORCE: -7.5,
    MOVE_SPEED: 1.5,
    COLORS: {
        SKY: "#5C94FC",
        MARIO: "#B83000",
        MARIO_SKIN: "#FFE0A8",
        MARIO_CLOTHES: "#000000",
        BRICK: "#BC4000",
        GROUND: "#80D010",
        COIN: "#F8D800",
        GOOMBA: "#704000"
    }
};

/**
 * MOTEUR AUDIO 8-BIT (Web Audio API)
 */
class AudioEngine {
    constructor() {
        this.ctx = null;
        this.enabled = false;
    }

    init() {
        if (this.enabled) return;
        this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        this.enabled = true;
    }

    /** Synthétise un son 8-bit */
    playNote(freq, duration, type = 'square', volume = 0.1) {
        if (!this.enabled) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        
        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
        
        gain.gain.setValueAtTime(volume, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);
        
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        
        osc.start();
        osc.stop(this.ctx.currentTime + duration);
    }

    playJump() { this.playNote(150, 0.2, 'square'); setTimeout(() => this.playNote(400, 0.2), 50); }
    playCoin() { this.playNote(987, 0.1); setTimeout(() => this.playNote(1318, 0.4), 100); }
    playStomp() { this.playNote(100, 0.1, 'sawtooth'); }
    playPowerUp() { [261, 329, 392, 523].forEach((f, i) => setTimeout(() => this.playNote(f, 0.2), i * 100)); }
    playHurt() { this.playNote(100, 0.5, 'sawtooth', 0.2); }
}

/**
 * GESTION DES SPRITES (Rendu procédural pixel art)
 */
class SpriteSheet {
    static drawTile(ctx, type, x, y) {
        ctx.save();
        ctx.translate(x, y);
        const s = CONFIG.TILE_SIZE;

        switch (type) {
            case 'G': // Ground
                ctx.fillStyle = CONFIG.COLORS.GROUND;
                ctx.fillRect(0, 0, s, s);
                ctx.strokeStyle = "rgba(0,0,0,0.2)";
                ctx.strokeRect(1, 1, s-2, s-2);
                break;
            case 'B': // Brick
                ctx.fillStyle = CONFIG.COLORS.BRICK;
                ctx.fillRect(0, 0, s, s);
                ctx.fillStyle = "rgba(0,0,0,0.3)";
                ctx.fillRect(0, s/2, s, 1);
                ctx.fillRect(s/2, 0, 1, s/2);
                break;
            case 'Q': // Question Block
                ctx.fillStyle = "#F87800";
                ctx.fillRect(0, 0, s, s);
                ctx.fillStyle = "#F8D800";
                ctx.fillText("?", 5, 12);
                break;
            case 'C': // Coin
                ctx.fillStyle = CONFIG.COLORS.COIN;
                ctx.beginPath();
                ctx.arc(s/2, s/2, 5, 0, Math.PI*2);
                ctx.fill();
                break;
        }
        ctx.restore();
    }

    static drawPlayer(ctx, x, y, frame, flip, state) {
        ctx.save();
        ctx.translate(x + (flip ? CONFIG.TILE_SIZE : 0), y);
        if (flip) ctx.scale(-1, 1);
        
        // Corps simplifié style NES
        ctx.fillStyle = CONFIG.COLORS.MARIO;
        ctx.fillRect(4, 4, 8, 12); // Tronc
        ctx.fillStyle = CONFIG.COLORS.MARIO_SKIN;
        ctx.fillRect(4, 0, 8, 6); // Tête
        ctx.fillStyle = CONFIG.COLORS.MARIO_CLOTHES;
        ctx.fillRect(4, 8, 8, 2); // Ceinture
        
        // Animation simple de course
        if (state === 'run' && frame % 10 < 5) {
            ctx.fillRect(2, 12, 4, 4);
        } else {
            ctx.fillRect(10, 12, 4, 4);
        }
        ctx.restore();
    }

    static drawEnemy(ctx, x, y, frame) {
        ctx.fillStyle = CONFIG.COLORS.GOOMBA;
        ctx.fillRect(x + 2, y + 4, 12, 12);
        ctx.fillStyle = "#FFF";
        ctx.fillRect(x + 4, y + 6, 2, 2);
        ctx.fillRect(x + 10, y + 6, 2, 2);
        // Animation de marche
        const offset = Math.sin(frame * 0.2) * 2;
        ctx.fillRect(x + 2, y + 14 + offset/2, 4, 2);
        ctx.fillRect(x + 10, y + 14 - offset/2, 4, 2);
    }
}

/**
 * LOGIQUE DU JOUEUR
 */
class Player {
    constructor() {
        this.reset();
    }

    reset() {
        this.x = 50;
        this.y = 150;
        this.vx = 0;
        this.vy = 0;
        this.width = 12;
        this.height = 16;
        this.grounded = false;
        this.flip = false;
        this.state = 'idle';
        this.score = 0;
        this.lives = 3;
        this.invulnerable = 0;
    }

    update(input, level) {
        if (this.invulnerable > 0) this.invulnerable--;

        // Contrôles
        if (input.left) {
            this.vx -= CONFIG.MOVE_SPEED * 0.2;
            this.flip = true;
            this.state = 'run';
        } else if (input.right) {
            this.vx += CONFIG.MOVE_SPEED * 0.2;
            this.flip = false;
            this.state = 'run';
        } else {
            this.vx *= CONFIG.FRICTION;
            this.state = 'idle';
        }

        if (input.jump && this.grounded) {
            this.vy = CONFIG.JUMP_FORCE;
            this.grounded = false;
            window.game.audio.playJump();
        }

        // Physique
        this.vy += CONFIG.GRAVITY;
        this.x += this.vx;
        this.checkCollision(level, 'x');
        this.y += this.vy;
        this.checkCollision(level, 'y');

        // Limites vitesse
        this.vx = Math.max(-CONFIG.MOVE_SPEED, Math.min(CONFIG.MOVE_SPEED, this.vx));

        // Mort par chute
        if (this.y > CONFIG.HEIGHT) this.die();
    }

    checkCollision(level, axis) {
        const tiles = level.getTilesInRect(this.x, this.y, this.width, this.height);
        for (let tile of tiles) {
            if (tile.type === 'G' || tile.type === 'B' || tile.type === 'Q') {
                if (axis === 'x') {
                    if (this.vx > 0) this.x = tile.x - this.width;
                    if (this.vx < 0) this.x = tile.x + CONFIG.TILE_SIZE;
                    this.vx = 0;
                } else {
                    if (this.vy > 0) {
                        this.y = tile.y - this.height;
                        this.grounded = true;
                        this.vy = 0;
                    } else if (this.vy < 0) {
                        this.y = tile.y + CONFIG.TILE_SIZE;
                        this.vy = 0;
                        if (tile.type === 'Q') level.collectCoin(tile.tx, tile.ty);
                    }
                }
            } else if (tile.type === 'C' && axis === 'y') {
                level.collectCoin(tile.tx, tile.ty);
            }
        }
    }

    die() {
        this.lives--;
        window.game.audio.playHurt();
        if (this.lives <= 0) window.game.gameOver();
        else this.reset();
    }
}

/**
 * GESTION DU NIVEAU
 */
class Level {
    constructor(data) {
        this.data = data.map(row => row.split(''));
        this.enemies = [];
        this.initEnemies();
    }

    initEnemies() {
        for (let y = 0; y < this.data.length; y++) {
            for (let x = 0; x < this.data[y].length; x++) {
                if (this.data[y][x] === 'E') {
                    this.enemies.push({ x: x * 16, y: y * 16, vx: -0.5, dead: false });
                    this.data[y][x] = ' ';
                }
            }
        }
    }

    getTilesInRect(x, y, w, h) {
        const tiles = [];
        const startX = Math.floor(x / 16);
        const endX = Math.floor((x + w) / 16);
        const startY = Math.floor(y / 16);
        const endY = Math.floor((y + h) / 16);

        for (let ty = startY; ty <= endY; ty++) {
            for (let tx = startX; tx <= endX; tx++) {
                if (this.data[ty] && this.data[ty][tx] && this.data[ty][tx] !== ' ') {
                    tiles.push({ x: tx * 16, y: ty * 16, type: this.data[ty][tx], tx, ty });
                }
            }
        }
        return tiles;
    }

    collectCoin(tx, ty) {
        this.data[ty][tx] = ' ';
        window.game.player.score += 100;
        window.game.audio.playCoin();
    }

    update(player) {
        this.enemies.forEach(en => {
            if (en.dead) return;
            en.x += en.vx;
            // Collision murs ennemis
            const tx = Math.floor((en.vx > 0 ? en.x + 16 : en.x) / 16);
            const ty = Math.floor((en.y + 8) / 16);
            if (this.data[ty] && this.data[ty][tx] !== ' ') en.vx *= -1;

            // Collision avec joueur
            const dx = player.x - en.x;
            const dy = player.y - en.y;
            if (Math.abs(dx) < 12 && Math.abs(dy) < 12) {
                if (player.vy > 0) {
                    en.dead = true;
                    player.vy = -4;
                    player.score += 200;
                    window.game.audio.playStomp();
                } else if (player.invulnerable <= 0) {
                    player.die();
                }
            }
        });
    }
}

/**
 * MOTEUR DE JEU PRINCIPAL
 */
class Game {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = CONFIG.WIDTH * CONFIG.SCALE;
        this.canvas.height = CONFIG.HEIGHT * CONFIG.SCALE;
        this.ctx.imageSmoothingEnabled = false;
        this.ctx.scale(CONFIG.SCALE, CONFIG.SCALE);
        document.body.appendChild(this.canvas);

        this.audio = new AudioEngine();
        this.player = new Player();
        this.input = { left: false, right: false, jump: false };
        this.levelIndex = 0;
        this.levels = [
            new Level([
                "                                        ",
                "                                        ",
                "    C  C                                ",
                "   BBBBBB        C                      ",
                "                BBB                     ",
                "                                        ",
                "         Q                              ",
                "                                     C  ",
                "      E      E            E         BBB ",
                "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
            ]),
            new Level([
                "                                        ",
                "   C  C  C                              ",
                "   BBBBBBB                              ",
                "            BBB     C                   ",
                "                 BBBBBB                 ",
                "       Q                  C             ",
                "                         BBB            ",
                "             E                          ",
                "      E     BBB      E          E       ",
                "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
            ])
        ];

        this.frame = 0;
        this.cameraX = 0;
        this.state = 'MENU';

        this.initEvents();
        this.loop();
    }

    initEvents() {
        window.addEventListener('keydown', e => {
            this.audio.init();
            if (this.state === 'MENU') this.state = 'PLAY';
            if (e.code === 'ArrowLeft') this.input.left = true;
            if (e.code === 'ArrowRight') this.input.right = true;
            if (e.code === 'Space') this.input.jump = true;
            if (e.code === 'KeyR') location.reload();
        });
        window.addEventListener('keyup', e => {
            if (e.code === 'ArrowLeft') this.input.left = false;
            if (e.code === 'ArrowRight') this.input.right = false;
            if (e.code === 'Space') this.input.jump = false;
        });
    }

    gameOver() {
        this.state = 'GAMEOVER';
        this.audio.playHurt();
    }

    update() {
        if (this.state !== 'PLAY') return;

        this.player.update(this.input, this.levels[this.levelIndex]);
        this.levels[this.levelIndex].update(this.player);

        // Camera follow
        const targetCamX = Math.max(0, this.player.x - CONFIG.WIDTH / 2);
        this.cameraX += (targetCamX - this.cameraX) * 0.1;

        // Win condition (fin du niveau)
        if (this.player.x > (this.levels[this.levelIndex].data[0].length * 16) - 32) {
            if (this.levelIndex < this.levels.length - 1) {
                this.levelIndex++;
                this.player.x = 50;
                this.audio.playPowerUp();
            } else {
                this.state = 'WIN';
            }
        }
    }

    draw() {
        // Background
        this.ctx.fillStyle = CONFIG.COLORS.SKY;
        this.ctx.fillRect(0, 0, CONFIG.WIDTH, CONFIG.HEIGHT);

        this.ctx.save();
        this.ctx.translate(-this.cameraX, 0);

        // Draw Level
        const currentLevel = this.levels[this.levelIndex];
        currentLevel.data.forEach((row, y) => {
            row.forEach((cell, x) => {
                if (cell !== ' ') SpriteSheet.drawTile(this.ctx, cell, x * 16, y * 16);
            });
        });

        // Draw Enemies
        currentLevel.enemies.forEach(en => {
            if (!en.dead) SpriteSheet.drawEnemy(this.ctx, en.x, en.y, this.frame);
        });

        // Draw Player
        if (this.player.invulnerable % 4 < 2) {
            SpriteSheet.drawPlayer(this.ctx, this.player.x, this.player.y, this.frame, this.player.flip, this.player.state);
        }

        this.ctx.restore();

        // UI
        this.drawUI();

        if (this.state === 'MENU') this.drawOverlay("MARIO HTML5", "PRESSEZ UNE TOUCHE");
        if (this.state === 'GAMEOVER') this.drawOverlay("GAME OVER", "R POUR RECOMMENCER");
        if (this.state === 'WIN') this.drawOverlay("BRAVO !", "VICTOIRE FINALE");
    }

    drawUI() {
        this.ctx.fillStyle = "#FFF";
        this.ctx.font = "8px 'Courier New'";
        this.ctx.fillText(`SCORE: ${this.player.score}`, 10, 20);
        this.ctx.fillText(`LIVES: ${this.player.lives}`, 10, 30);
        this.ctx.fillText(`WORLD: 1-${this.levelIndex + 1}`, CONFIG.WIDTH - 60, 20);
    }

    drawOverlay(title, subtitle) {
        this.ctx.fillStyle = "rgba(0,0,0,0.5)";
        this.ctx.fillRect(0, 0, CONFIG.WIDTH, CONFIG.HEIGHT);
        this.ctx.fillStyle = "#FFF";
        this.ctx.textAlign = "center";
        this.ctx.font = "16px 'Courier New'";
        this.ctx.fillText(title, CONFIG.WIDTH / 2, CONFIG.HEIGHT / 2 - 10);
        this.ctx.font = "8px 'Courier New'";
        this.ctx.fillText(subtitle, CONFIG.WIDTH / 2, CONFIG.HEIGHT / 2 + 10);
        this.ctx.textAlign = "left";
    }

    loop() {
        this.frame++;
        this.update();
        this.draw();
        requestAnimationFrame(() => this.loop());
    }
}

// Initialisation globale
window.game = new Game();

// CSS pour un rendu propre
const style = document.createElement('style');
style.textContent = `
    body { 
        background: #222; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        height: 100vh; 
        margin: 0; 
        overflow: hidden;
    }
    canvas { 
        border: 4px solid #000; 
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        image-rendering: pixelated;
    }
`;
document.head.appendChild(style);