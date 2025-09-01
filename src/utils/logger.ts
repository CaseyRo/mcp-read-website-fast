import chalk from 'chalk';

export enum LogLevel {
    ERROR = 0,
    WARN = 1,
    INFO = 2,
    DEBUG = 3,
}

export class Logger {
    private level: LogLevel;
    private name: string;
    private quiet: boolean;

    constructor(name: string, level: LogLevel = LogLevel.INFO) {
        this.name = name;
        this.level = level;
        // In MCP mode, only output errors unless explicitly in debug mode
        this.quiet =
            process.env.MCP_QUIET === 'true' ||
            (!process.env.MCP_DEBUG && this.name === 'MCP');
    }

    private log(level: LogLevel, message: string, ...args: any[]): void {
        if (level > this.level) return;

        // In quiet mode, only output errors
        if (this.quiet && level !== LogLevel.ERROR) return;

        const timestamp = new Date().toISOString();
        const levelName = LogLevel[level];
        const prefix = `[${timestamp}] [${levelName}] [${this.name}]`;

        // Color coding for different log levels
        let coloredPrefix: string;
        let coloredMessage: string;

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

        // Always use stderr for MCP servers to avoid stdout conflicts
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

    error(message: string, ...args: any[]): void {
        this.log(LogLevel.ERROR, `❌ ${message}`, ...args);
    }

    warn(message: string, ...args: any[]): void {
        this.log(LogLevel.WARN, `⚠️  ${message}`, ...args);
    }

    info(message: string, ...args: any[]): void {
        this.log(LogLevel.INFO, `ℹ️  ${message}`, ...args);
    }

    debug(message: string, ...args: any[]): void {
        this.log(LogLevel.DEBUG, `🔍 ${message}`, ...args);
    }

    success(message: string, ...args: any[]): void {
        this.log(LogLevel.INFO, `✅ ${message}`, ...args);
    }

    // Special method for logging markdown preview
    markdownPreview(content: string, maxLength: number = 200): void {
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

    setLevel(level: LogLevel): void {
        this.level = level;
    }
}

// Global logger instance
export const logger = new Logger('MCP');

// Set log level from environment
const envLevel = process.env.LOG_LEVEL?.toUpperCase();
if (envLevel && envLevel in LogLevel) {
    logger.setLevel(
        LogLevel[envLevel as keyof typeof LogLevel] as unknown as LogLevel
    );
}
