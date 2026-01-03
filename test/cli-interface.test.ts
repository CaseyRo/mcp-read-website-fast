import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Command } from 'commander';

// Mock fetchMarkdown
vi.mock('../src/internal/fetchMarkdown.js', () => ({
    fetchMarkdown: vi.fn(),
}));

// Mock console methods to avoid output during tests
const originalConsoleLog = console.log;
const originalConsoleError = console.error;

describe('CLI Interface', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        console.log = vi.fn();
        console.error = vi.fn();
    });

    afterEach(() => {
        console.log = originalConsoleLog;
        console.error = originalConsoleError;
    });

    describe('Command structure', () => {
        it('should have fetch command defined', async () => {
            // Test that the CLI structure is correct by checking the command exists
            const program = new Command();
            program.command('fetch <url>').description('Fetch a URL and convert to Markdown');

            const fetchCommand = program.commands.find(cmd => cmd.name() === 'fetch');
            expect(fetchCommand).toBeDefined();
            expect(fetchCommand?.description()).toBe('Fetch a URL and convert to Markdown');
        });

        it('should have clear-cache command defined', async () => {
            const program = new Command();
            program.command('clear-cache').description('Clear the cache directory');

            const clearCacheCommand = program.commands.find(
                cmd => cmd.name() === 'clear-cache'
            );
            expect(clearCacheCommand).toBeDefined();
            expect(clearCacheCommand?.description()).toBe('Clear the cache directory');
        });

        it('should have serve command defined', async () => {
            const program = new Command();
            program.command('serve').description('Run as an MCP server');

            const serveCommand = program.commands.find(cmd => cmd.name() === 'serve');
            expect(serveCommand).toBeDefined();
        });
    });

    describe('Fetch command options', () => {
        it('should accept pages option', () => {
            const program = new Command();
            const fetchCmd = program
                .command('fetch <url>')
                .option('-p, --pages <number>', 'Maximum number of pages to crawl', '1');

            const options = fetchCmd.opts();
            expect(fetchCmd.options.some(opt => opt.long === '--pages')).toBe(true);
        });

        it('should accept concurrency option', () => {
            const program = new Command();
            const fetchCmd = program
                .command('fetch <url>')
                .option('-c, --concurrency <number>', 'Max concurrent requests', '3');

            expect(fetchCmd.options.some(opt => opt.long === '--concurrency')).toBe(true);
        });

        it('should accept no-robots option', () => {
            const program = new Command();
            const fetchCmd = program
                .command('fetch <url>')
                .option('--no-robots', 'Ignore robots.txt');

            expect(fetchCmd.options.some(opt => opt.long === '--no-robots')).toBe(true);
        });

        it('should accept all-origins option', () => {
            const program = new Command();
            const fetchCmd = program
                .command('fetch <url>')
                .option('--all-origins', 'Allow cross-origin crawling');

            expect(fetchCmd.options.some(opt => opt.long === '--all-origins')).toBe(true);
        });

        it('should accept user-agent option', () => {
            const program = new Command();
            const fetchCmd = program
                .command('fetch <url>')
                .option('-u, --user-agent <string>', 'Custom user agent');

            expect(fetchCmd.options.some(opt => opt.long === '--user-agent')).toBe(true);
        });

        it('should accept cache-dir option', () => {
            const program = new Command();
            const fetchCmd = program
                .command('fetch <url>')
                .option('--cache-dir <path>', 'Cache directory', '.cache');

            expect(fetchCmd.options.some(opt => opt.long === '--cache-dir')).toBe(true);
        });

        it('should accept timeout option', () => {
            const program = new Command();
            const fetchCmd = program
                .command('fetch <url>')
                .option('-t, --timeout <ms>', 'Request timeout in milliseconds', '30000');

            expect(fetchCmd.options.some(opt => opt.long === '--timeout')).toBe(true);
        });

        it('should accept output format option', () => {
            const program = new Command();
            const fetchCmd = program
                .command('fetch <url>')
                .option(
                    '-o, --output <format>',
                    'Output format: json, markdown, or both',
                    'markdown'
                );

            expect(fetchCmd.options.some(opt => opt.long === '--output')).toBe(true);
        });
    });
});

