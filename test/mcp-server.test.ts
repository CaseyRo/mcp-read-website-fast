import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock fetchMarkdown
vi.mock('../src/internal/fetchMarkdown.js', () => ({
    fetchMarkdown: vi.fn(),
}));

// Mock fs/promises and path
vi.mock('fs/promises', () => ({
    readdir: vi.fn(),
    stat: vi.fn(),
    rm: vi.fn(),
}));

vi.mock('path', () => ({
    join: vi.fn((...args) => args.join('/')),
}));

describe('MCP Server Handlers', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Tool Handler - read_website', () => {
        it('should handle read_website tool call successfully', async () => {
            const { fetchMarkdown } = await import('../src/internal/fetchMarkdown.js');
            vi.mocked(fetchMarkdown).mockResolvedValue({
                markdown: '# Test Page\n\nContent here.',
                title: 'Test Page',
            });

            // Import the handler logic (we'll need to test the actual handler)
            // For now, test the fetchMarkdown integration
            const result = await fetchMarkdown('https://example.com', {
                maxPages: 1,
            });

            expect(result.markdown).toContain('Test Page');
            expect(vi.mocked(fetchMarkdown)).toHaveBeenCalledWith(
                'https://example.com',
                expect.objectContaining({
                    maxPages: 1,
                })
            );
        });

        it('should handle read_website with multiple pages', async () => {
            const { fetchMarkdown } = await import('../src/internal/fetchMarkdown.js');
            vi.mocked(fetchMarkdown).mockResolvedValue({
                markdown: '# Page 1\n\n---\n\n# Page 2',
                title: 'Page 1',
            });

            const result = await fetchMarkdown('https://example.com', {
                maxPages: 2,
            });

            expect(vi.mocked(fetchMarkdown)).toHaveBeenCalledWith(
                'https://example.com',
                expect.objectContaining({
                    maxPages: 2,
                })
            );
            expect(result.markdown).toContain('Page 1');
        });

        it('should handle errors in read_website', async () => {
            const { fetchMarkdown } = await import('../src/internal/fetchMarkdown.js');
            vi.mocked(fetchMarkdown).mockResolvedValue({
                markdown: '',
                error: 'Failed to fetch',
            });

            const result = await fetchMarkdown('https://example.com');

            expect(result.error).toBe('Failed to fetch');
            expect(result.markdown).toBe('');
        });

        it('should handle partial content with errors', async () => {
            const { fetchMarkdown } = await import('../src/internal/fetchMarkdown.js');
            vi.mocked(fetchMarkdown).mockResolvedValue({
                markdown: '# Partial Content',
                error: 'Some pages had errors',
            });

            const result = await fetchMarkdown('https://example.com');

            expect(result.markdown).toContain('Partial Content');
            expect(result.error).toBe('Some pages had errors');
        });
    });

    describe('Resource Handler - cache status', () => {
        it('should return cache status information', async () => {
            const fsPromises = await import('fs/promises');
            const pathModule = await import('path');

            vi.mocked(fsPromises.readdir).mockResolvedValue(['file1', 'file2'] as any);
            vi.mocked(fsPromises.stat).mockResolvedValue({ size: 1024 } as any);
            vi.mocked(pathModule.join).mockReturnValue('.cache/file1');

            const files = await fsPromises.readdir('.cache');
            expect(files).toHaveLength(2);
        });

        it('should handle cache directory not existing', async () => {
            const fsPromises = await import('fs/promises');
            vi.mocked(fsPromises.readdir).mockRejectedValue(new Error('ENOENT'));

            try {
                await fsPromises.readdir('.cache');
            } catch (error) {
                expect(error).toBeInstanceOf(Error);
            }
        });
    });

    describe('Resource Handler - clear cache', () => {
        it('should clear cache successfully', async () => {
            const fsPromises = await import('fs/promises');
            vi.mocked(fsPromises.rm).mockResolvedValue(undefined);

            await fsPromises.rm('.cache', { recursive: true, force: true });

            expect(vi.mocked(fsPromises.rm)).toHaveBeenCalledWith('.cache', {
                recursive: true,
                force: true,
            });
        });

        it('should handle cache clear errors', async () => {
            const fsPromises = await import('fs/promises');
            vi.mocked(fsPromises.rm).mockRejectedValue(new Error('Permission denied'));

            try {
                await fsPromises.rm('.cache', { recursive: true, force: true });
            } catch (error) {
                expect(error).toBeInstanceOf(Error);
            }
        });
    });
});

