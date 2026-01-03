export function extractMarkdownLinks(markdown, baseUrl) {
    const links = [];
    const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    const bareUrlRegex = /https?:\/\/[^\s<>)\]]+/g;
    let match;
    while ((match = markdownLinkRegex.exec(markdown)) !== null) {
        const url = match[2];
        if (url &&
            !url.startsWith('#') &&
            !url.startsWith('mailto:') &&
            !url.startsWith('tel:')) {
            links.push(url);
        }
    }
    while ((match = bareUrlRegex.exec(markdown)) !== null) {
        links.push(match[0]);
    }
    const absoluteLinks = links
        .map(link => {
        try {
            if (link.startsWith('http://') || link.startsWith('https://')) {
                return link;
            }
            return new URL(link, baseUrl).href;
        }
        catch {
            return null;
        }
    })
        .filter(Boolean);
    return [...new Set(absoluteLinks)];
}
export function filterSameOriginLinks(links, baseUrl) {
    try {
        const baseOrigin = new URL(baseUrl).origin;
        return links.filter(link => {
            try {
                return new URL(link).origin === baseOrigin;
            }
            catch {
                return false;
            }
        });
    }
    catch {
        return [];
    }
}
