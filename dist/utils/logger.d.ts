export declare enum LogLevel {
    ERROR = 0,
    WARN = 1,
    INFO = 2,
    DEBUG = 3
}
export declare class Logger {
    private level;
    private name;
    private quiet;
    constructor(name: string, level?: LogLevel);
    private log;
    error(message: string, ...args: any[]): void;
    warn(message: string, ...args: any[]): void;
    info(message: string, ...args: any[]): void;
    debug(message: string, ...args: any[]): void;
    success(message: string, ...args: any[]): void;
    markdownPreview(content: string, maxLength?: number): void;
    setLevel(level: LogLevel): void;
}
export declare const logger: Logger;
