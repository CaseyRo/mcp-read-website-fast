export interface FetchMarkdownOptions {
    depth?: number;
    maxConcurrency?: number;
    respectRobots?: boolean;
    sameOriginOnly?: boolean;
    userAgent?: string;
    cacheDir?: string;
    timeout?: number;
    maxPages?: number;
    cookiesFile?: string;
}
export interface FetchMarkdownResult {
    markdown: string;
    title?: string;
    links?: string[];
    error?: string;
}
export declare function fetchMarkdown(url: string, options?: FetchMarkdownOptions): Promise<FetchMarkdownResult>;
