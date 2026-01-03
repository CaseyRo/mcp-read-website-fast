import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchMarkdown } from '../src/internal/fetchMarkdown.js';

// Mock @just-every/crawl
vi.mock('@just-every/crawl', () => ({
    fetch: vi.fn(),
}));

// Mock extractMarkdownLinks
vi.mock('../src/utils/extractMarkdownLinks.js', () => ({
    extractMarkdownLinks: vi.fn((markdown: string) => {
        // Simple mock: extract links from markdown
        const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        const links: string[] = [];
        let match;
        while ((match = linkRegex.exec(markdown)) !== null) {
            links.push(match[2]);
        }
        return links;
    }),
    filterSameOriginLinks: vi.fn((links: string[], baseUrl: string) => {
        const base = new URL(baseUrl);
        return links.filter(link => {
            try {
                const linkUrl = new URL(link, baseUrl);
                return linkUrl.origin === base.origin;
            } catch {
                return false;
            }
        });
    }),
}));

describe('fetchMarkdown', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('success cases', () => {
        it('should fetch a single page successfully', async () => {
            const { fetch } = await import('@just-every/crawl');
            vi.mocked(fetch).mockResolvedValue([
                {
                    url: 'https://example.com',
                    markdown: '# Example Page\n\nThis is test content.',
                    title: 'Example Page',
                    links: [],
                },
            ]);

            const result = await fetchMarkdown('https://example.com');

            expect(result.markdown).toContain('Example Page');
            expect(result.markdown).toContain('This is test content');
            expect(result.title).toBe('Example Page');
            expect(result.error).toBeUndefined();
        });

        it('should include source URL comment in markdown', async () => {
            const { fetch } = await import('@just-every/crawl');
            vi.mocked(fetch).mockResolvedValue([
                {
                    url: 'https://example.com/article',
                    markdown: '# Article Title\n\nContent here.',
                    title: 'Article Title',
                    links: [],
                },
            ]);

            const result = await fetchMarkdown('https://example.com/article');

            expect(result.markdown).toContain('<!-- Source: https://example.com/article -->');
        });

        it('should handle multiple pages with separators', async () => {
            const { fetch } = await import('@just-every/crawl');
            const { extractMarkdownLinks } = await import('../src/utils/extractMarkdownLinks.js');

            // First page with a link
            vi.mocked(fetch)
                .mockResolvedValueOnce([
                    {
                        url: 'https://example.com/page1',
                        markdown: '# Page 1\n\n[Link to page 2](/page2)',
                        title: 'Page 1',
                        links: [],
                    },
                ])
                .mockResolvedValueOnce([
                    {
                        url: 'https://example.com/page2',
                        markdown: '# Page 2\n\nContent here.',
                        title: 'Page 2',
                        links: [],
                    },
                ]);

            vi.mocked(extractMarkdownLinks).mockReturnValue(['https://example.com/page2']);

            const result = await fetchMarkdown('https://example.com/page1', { maxPages: 2 });

            expect(result.markdown).toContain('Page 1');
            expect(result.markdown).toContain('Page 2');
            expect(result.markdown).toContain('---'); // Page separator
        });

        it('should respect maxPages limit', async () => {
            const { fetch } = await import('@just-every/crawl');
            const { extractMarkdownLinks } = await import('../src/utils/extractMarkdownLinks.js');

            vi.mocked(fetch).mockResolvedValue([
                {
                    url: 'https://example.com',
                    markdown: '# Page\n\n[Link](/page2)',
                    title: 'Page',
                    links: [],
                },
            ]);

            vi.mocked(extractMarkdownLinks).mockReturnValue([
                'https://example.com/page2',
                'https://example.com/page3',
            ]);

            const result = await fetchMarkdown('https://example.com', { maxPages: 1 });

            expect(vi.mocked(fetch)).toHaveBeenCalledTimes(1);
            expect(result.markdown).toContain('Page');
        });

        it('should use provided options', async () => {
            const { fetch } = await import('@just-every/crawl');
            vi.mocked(fetch).mockResolvedValue([
                {
                    url: 'https://example.com',
                    markdown: '# Test',
                    title: 'Test',
                    links: [],
                },
            ]);

            await fetchMarkdown('https://example.com', {
                respectRobots: false,
                sameOriginOnly: false,
                userAgent: 'CustomAgent',
                cacheDir: '/custom/cache',
                timeout: 60000,
                maxConcurrency: 5,
            });

            expect(vi.mocked(fetch)).toHaveBeenCalledWith(
                'https://example.com',
                expect.objectContaining({
                    respectRobots: false,
                    sameOriginOnly: false,
                    userAgent: 'CustomAgent',
                    cacheDir: '/custom/cache',
                    timeout: 60000,
                    maxConcurrency: 5,
                })
            );
        });
    });

    describe('error cases', () => {
        it('should return error when no results are returned', async () => {
            const { fetch } = await import('@just-every/crawl');
            vi.mocked(fetch).mockResolvedValue([]);

            const result = await fetchMarkdown('https://example.com');

            expect(result.markdown).toBe('');
            expect(result.error).toBe('No results returned');
        });

        it('should handle fetch errors gracefully', async () => {
            const { fetch } = await import('@just-every/crawl');
            vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

            const result = await fetchMarkdown('https://example.com');

            expect(result.markdown).toBe('');
            expect(result.error).toBe('Network error');
        });

        it('should handle pages with errors', async () => {
            const { fetch } = await import('@just-every/crawl');
            const { extractMarkdownLinks } = await import('../src/utils/extractMarkdownLinks.js');

            // First call returns page 1, second call returns page 2 with error
            vi.mocked(fetch)
                .mockResolvedValueOnce([
                    {
                        url: 'https://example.com',
                        markdown: '# Page 1\n\n[Link](/page2)',
                        title: 'Page 1',
                        links: [],
                    },
                ])
                .mockResolvedValueOnce([
                    {
                        url: 'https://example.com/page2',
                        error: 'Failed to fetch',
                        markdown: '',
                    },
                ]);

            vi.mocked(extractMarkdownLinks).mockReturnValue(['https://example.com/page2']);

            const result = await fetchMarkdown('https://example.com', { maxPages: 2 });

            expect(result.markdown).toContain('Page 1');
            expect(result.markdown).toContain('Error fetching');
            expect(result.error).toContain('Some pages had errors');
        });

        it('should handle unknown errors', async () => {
            const { fetch } = await import('@just-every/crawl');
            vi.mocked(fetch).mockRejectedValue('Unknown error');

            const result = await fetchMarkdown('https://example.com');

            expect(result.markdown).toBe('');
            expect(result.error).toBe('Unknown error');
        });
    });
});

