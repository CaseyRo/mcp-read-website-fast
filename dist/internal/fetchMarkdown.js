import { fetch } from '@just-every/crawl';
import { extractMarkdownLinks, filterSameOriginLinks, } from '../utils/extractMarkdownLinks.js';
export async function fetchMarkdown(url, options = {}) {
    try {
        const maxPages = options.maxPages ?? 1;
        const visited = new Set();
        const toVisit = [url];
        const allResults = [];
        while (toVisit.length > 0 && allResults.length < maxPages) {
            const currentUrl = toVisit.shift();
            if (visited.has(currentUrl))
                continue;
            visited.add(currentUrl);
            const crawlOptions = {
                depth: 0,
                maxConcurrency: options.maxConcurrency ?? 3,
                respectRobots: options.respectRobots ?? true,
                sameOriginOnly: options.sameOriginOnly ?? true,
                userAgent: options.userAgent,
                cacheDir: options.cacheDir ?? '.cache',
                timeout: options.timeout ?? 30000,
            };
            if (options.cookiesFile) {
                crawlOptions.cookiesFile = options.cookiesFile;
            }
            const results = await fetch(currentUrl, crawlOptions);
            if (results && results.length > 0) {
                const result = results[0];
                allResults.push(result);
                if (allResults.length < maxPages && result.markdown) {
                    const links = extractMarkdownLinks(result.markdown, currentUrl);
                    const filteredLinks = options.sameOriginOnly !== false
                        ? filterSameOriginLinks(links, currentUrl)
                        : links;
                    for (const link of filteredLinks) {
                        if (!visited.has(link) && !toVisit.includes(link)) {
                            toVisit.push(link);
                        }
                    }
                }
            }
        }
        if (allResults.length === 0) {
            return {
                markdown: '',
                error: 'No results returned',
            };
        }
        const pagesToReturn = allResults;
        const combinedMarkdown = pagesToReturn
            .map((result, index) => {
            if (result.error) {
                return `<!-- Error fetching ${result.url}: ${result.error} -->`;
            }
            let pageContent = '';
            if (pagesToReturn.length > 1 && index > 0) {
                pageContent += '\n\n---\n\n';
            }
            pageContent += `<!-- Source: ${result.url} -->\n`;
            pageContent += result.markdown || '';
            return pageContent;
        })
            .join('\n');
        return {
            markdown: combinedMarkdown,
            title: pagesToReturn[0].title,
            links: pagesToReturn.flatMap(r => r.links || []),
            error: pagesToReturn.some(r => r.error)
                ? `Some pages had errors: ${pagesToReturn
                    .filter(r => r.error)
                    .map(r => r.url)
                    .join(', ')}`
                : undefined,
        };
    }
    catch (error) {
        return {
            markdown: '',
            error: error instanceof Error ? error.message : 'Unknown error',
        };
    }
}
