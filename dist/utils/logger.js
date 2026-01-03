import chalk from 'chalk';
export var LogLevel;
(function (LogLevel) {
    LogLevel[LogLevel["ERROR"] = 0] = "ERROR";
    LogLevel[LogLevel["WARN"] = 1] = "WARN";
    LogLevel[LogLevel["INFO"] = 2] = "INFO";
    LogLevel[LogLevel["DEBUG"] = 3] = "DEBUG";
})(LogLevel || (LogLevel = {}));
export class Logger {
    level;
    name;
    quiet;
    constructor(name, level = LogLevel.INFO) {
        this.name = name;
        this.level = level;
        this.quiet =
            process.env.MCP_QUIET === 'true' ||
                (!process.env.MCP_DEBUG && this.name === 'MCP');
    }
    log(level, message, ...args) {
        if (level > this.level)
            return;
        if (this.quiet && level !== LogLevel.ERROR)
            return;
        const timestamp = new Date().toISOString();
        const levelName = LogLevel[level];
        const prefix = `[${timestamp}] [${levelName}] [${this.name}]`;
        let coloredPrefix;
        let coloredMessage;
        switch (level) {
            case LogLevel.ERROR:
                coloredPrefix = chalk.red.bold(prefix);
                coloredMessage = chalk.red(message);
                break;
            case LogLevel.WARN:
                coloredPrefix = chalk.yellow.bold(prefix);
                coloredMessage = chalk.yellow(message);
                break;
            case LogLevel.INFO:
                coloredPrefix = chalk.blue.bold(prefix);
                coloredMessage = chalk.cyan(message);
                break;
            default:
                coloredPrefix = chalk.gray(prefix);
                coloredMessage = chalk.gray(message);
        }
        switch (level) {
            case LogLevel.ERROR:
                console.error(coloredPrefix, coloredMessage, ...args);
                break;
            case LogLevel.WARN:
                console.error(coloredPrefix, coloredMessage, ...args);
                break;
            default:
                console.error(coloredPrefix, coloredMessage, ...args);
        }
    }
    error(message, ...args) {
        this.log(LogLevel.ERROR, `❌ ${message}`, ...args);
    }
    warn(message, ...args) {
        this.log(LogLevel.WARN, `⚠️  ${message}`, ...args);
    }
    info(message, ...args) {
        this.log(LogLevel.INFO, `ℹ️  ${message}`, ...args);
    }
    debug(message, ...args) {
        this.log(LogLevel.DEBUG, `🔍 ${message}`, ...args);
    }
    success(message, ...args) {
        this.log(LogLevel.INFO, `✅ ${message}`, ...args);
    }
    markdownPreview(content, maxLength = 200) {
        if (this.level >= LogLevel.INFO) {
            const preview = content.substring(0, maxLength);
            const truncated = content.length > maxLength;
            const previewText = truncated ? `${preview}...` : preview;
            console.error(chalk.green.bold('📄 Markdown Preview:'));
            console.error(chalk.gray('─'.repeat(50)));
            console.error(chalk.white(previewText));
            if (truncated) {
                console.error(chalk.gray(`... (truncated, total length: ${content.length} chars)`));
            }
            console.error(chalk.gray('─'.repeat(50)));
        }
    }
    setLevel(level) {
        this.level = level;
    }
}
export const logger = new Logger('MCP');
const envLevel = process.env.LOG_LEVEL?.toUpperCase();
if (envLevel && envLevel in LogLevel) {
    logger.setLevel(LogLevel[envLevel]);
}
