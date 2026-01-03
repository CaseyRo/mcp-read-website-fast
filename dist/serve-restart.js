#!/usr/bin/env node
import { spawn } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
const __dirname = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--port' || arg === '-p') {
        const value = args[i + 1];
        if (value)
            process.env.PORT = value;
    }
    else if (arg.startsWith('--port=')) {
        process.env.PORT = arg.split('=')[1];
    }
}
const MAX_RESTART_ATTEMPTS = 10;
const RESTART_WINDOW_MS = 60000;
const INITIAL_BACKOFF_MS = 1000;
const MAX_BACKOFF_MS = 30000;
let restartAttempts = [];
let currentBackoff = INITIAL_BACKOFF_MS;
const log = (level, message, ...args) => {
    const timestamp = new Date().toISOString();
    console.error(`[${timestamp}] [${level}] [restart-wrapper]`, message, ...args);
};
const cleanupRestartAttempts = () => {
    const now = Date.now();
    restartAttempts = restartAttempts.filter(timestamp => now - timestamp < RESTART_WINDOW_MS);
};
const shouldRestart = () => {
    cleanupRestartAttempts();
    if (restartAttempts.length >= MAX_RESTART_ATTEMPTS) {
        log('ERROR', `Reached maximum restart attempts (${MAX_RESTART_ATTEMPTS}) within ${RESTART_WINDOW_MS}ms`);
        return false;
    }
    return true;
};
const getBackoffDelay = () => {
    const delay = Math.min(currentBackoff, MAX_BACKOFF_MS);
    currentBackoff = Math.min(currentBackoff * 2, MAX_BACKOFF_MS);
    return delay;
};
const resetBackoff = () => {
    currentBackoff = INITIAL_BACKOFF_MS;
};
const startServer = () => {
    log('INFO', 'Starting MCP server...');
    const serverPath = join(__dirname, 'serve.js');
    const child = spawn(process.execPath, [serverPath], {
        stdio: ['inherit', 'inherit', 'pipe'],
        env: process.env,
    });
    let shuttingDown = false;
    child.stderr?.on('data', data => {
        process.stderr.write(data);
    });
    let restartTimer = null;
    const startupTimer = setTimeout(() => {
        log('INFO', 'Server started successfully');
        resetBackoff();
    }, 5000);
    child.on('exit', (code, signal) => {
        clearTimeout(startupTimer);
        if (shuttingDown) {
            log('INFO', 'Server stopped gracefully');
            process.exit(0);
            return;
        }
        if (code === 0) {
            log('INFO', 'Server exited cleanly');
            process.exit(0);
            return;
        }
        log('WARN', `Server exited with code ${code}, signal ${signal}`);
        if (!shouldRestart()) {
            log('ERROR', 'Too many restart attempts, giving up');
            process.exit(1);
            return;
        }
        const backoffDelay = getBackoffDelay();
        restartAttempts.push(Date.now());
        log('INFO', `Restarting server in ${backoffDelay}ms (attempt ${restartAttempts.length}/${MAX_RESTART_ATTEMPTS})...`);
        restartTimer = setTimeout(() => {
            startServer();
        }, backoffDelay);
    });
    child.on('error', error => {
        log('ERROR', 'Failed to start server:', error);
        process.exit(1);
    });
    const shutdown = (signal) => {
        if (shuttingDown)
            return;
        shuttingDown = true;
        log('INFO', `Received ${signal}, shutting down...`);
        if (restartTimer) {
            clearTimeout(restartTimer);
        }
        child.kill(signal);
        setTimeout(() => {
            log('WARN', 'Force killing child process');
            child.kill('SIGKILL');
        }, 5000);
    };
    process.on('SIGINT', () => shutdown('SIGINT'));
    process.on('SIGTERM', () => shutdown('SIGTERM'));
};
process.on('uncaughtException', error => {
    log('ERROR', 'Uncaught exception in restart wrapper:', error);
    process.exit(1);
});
process.on('unhandledRejection', reason => {
    log('ERROR', 'Unhandled rejection in restart wrapper:', reason);
    process.exit(1);
});
log('INFO', 'MCP server restart wrapper starting...');
log('INFO', `Configuration: max attempts=${MAX_RESTART_ATTEMPTS}, window=${RESTART_WINDOW_MS}ms`);
startServer();
