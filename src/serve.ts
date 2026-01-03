#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { createServer } from 'node:http';
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
    ListResourcesRequestSchema,
    ReadResourceRequestSchema,
    type Tool,
    type Resource,
} from '@modelcontextprotocol/sdk/types.js';
import { logger } from './utils/logger.js';

// MCP server logger will automatically be quiet unless MCP_DEBUG is set
logger.info('🚀 MCP Server starting up...');
logger.debug('Node version:', process.version);
logger.debug('Working directory:', process.cwd());
logger.debug('Environment:', { LOG_LEVEL: process.env.LOG_LEVEL });

// Ensure the process doesn't exit on stderr errors
process.stderr.on('error', () => {});

// Lazy load heavy dependencies
let fetchMarkdownModule: any;
let fsPromises: any;
let pathModule: any;

logger.debug('🔧 Creating MCP server instance...');
const server = new Server(
    {
        name: 'read-website-fast',
        version: '0.1.21',
    },
    {
        capabilities: {
            tools: {},
            resources: {},
        },
    }
);
logger.success('MCP server instance created successfully');

// Add error handling for the server instance
server.onerror = error => {
    logger.error('MCP Server Error:', error);
};

// Tool definition
const READ_WEBSITE_TOOL: Tool = {
    name: 'read_website',
    description:
        'Fast, token-efficient web content extraction - ideal for reading documentation, analyzing content, and gathering information from websites. Converts to clean Markdown while preserving links and structure. Supports optional output formats: "markdown" (default), "json" (structured data), or "both" (markdown + JSON).',
    inputSchema: {
        type: 'object',
        properties: {
            url: {
                type: 'string',
                description: 'HTTP/HTTPS URL to fetch and convert to markdown',
            },
            pages: {
                type: 'number',
                description: 'Maximum number of pages to crawl (default: 1)',
                default: 1,
                minimum: 1,
                maximum: 100,
            },
            cookiesFile: {
                type: 'string',
                description:
                    'Path to Netscape cookie file for authenticated pages',
                optional: true,
            },
            output: {
                type: 'string',
                description:
                    'Output format: "markdown" (default, human-readable text), "json" (structured data with metadata), or "both" (returns both formats)',
                enum: ['markdown', 'json', 'both'],
                default: 'markdown',
                optional: true,
            },
        },
        required: ['url'],
    },
    annotations: {
        title: 'Read Website',
        readOnlyHint: true, // Only reads content
        destructiveHint: false,
        idempotentHint: true, // Same URL returns same content (with cache)
        openWorldHint: true, // Interacts with external websites
    },
};

// Resources definitions
const RESOURCES: Resource[] = [
    {
        uri: 'read-website-fast://status',
        name: 'Cache Status',
        mimeType: 'application/json',
        description: 'Get cache status information',
    },
    {
        uri: 'read-website-fast://clear-cache',
        name: 'Clear Cache',
        mimeType: 'application/json',
        description: 'Clear the cache directory',
    },
];

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
    logger.debug('Received ListTools request');
    const response = {
        tools: [READ_WEBSITE_TOOL],
    };
    logger.debug(
        'Returning tools:',
        response.tools.map(t => t.name)
    );
    return response;
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async request => {
    logger.info('Received CallTool request:', request.params.name);
    logger.debug('Request params:', JSON.stringify(request.params, null, 2));

    if (request.params.name !== 'read_website') {
        const error = `Unknown tool: ${request.params.name}`;
        logger.error(error);
        throw new Error(error);
    }

    try {
        // Lazy load the module on first use
        if (!fetchMarkdownModule) {
            logger.debug('Lazy loading fetchMarkdown module...');
            fetchMarkdownModule = await import('./internal/fetchMarkdown.js');
            logger.info('fetchMarkdown module loaded successfully');
        }

        const args = request.params.arguments as any;

        // Validate URL
        if (!args.url || typeof args.url !== 'string') {
            throw new Error('URL parameter is required and must be a string');
        }

        // Validate and get output format
        const outputFormat = args.output || 'markdown';
        if (!['markdown', 'json', 'both'].includes(outputFormat)) {
            throw new Error(
                `Invalid output format: ${outputFormat}. Must be "markdown", "json", or "both"`
            );
        }

        logger.info(`Processing read request for URL: ${args.url}`);
        logger.debug('Read parameters:', {
            url: args.url,
            pages: args.pages,
            cookiesFile: args.cookiesFile,
            output: outputFormat,
        });

        logger.debug('Calling fetchMarkdown...');

        // Convert pages to depth (pages - 1 = depth)
        // pages: 1 = depth: 0 (single page)
        // pages: 2+ = depth: 1 (crawl one level to get multiple pages)
        const depth = args.pages > 1 ? 1 : 0;

        const result = await fetchMarkdownModule.fetchMarkdown(args.url, {
            depth: depth,
            respectRobots: false, // Default to not respecting robots.txt
            maxPages: args.pages ?? 1,
            cookiesFile: args.cookiesFile,
        });
        logger.success('✅ Content fetched successfully');

        // Show markdown preview when LOG_LEVEL is info or higher
        if (result.markdown) {
            logger.markdownPreview(result.markdown, 300);
        }

        // Prepare JSON output structure
        const jsonData = {
            markdown: result.markdown || '',
            title: result.title,
            links: result.links || [],
            url: args.url,
            error: result.error,
        };

        // Format response based on output format
        if (outputFormat === 'json') {
            // JSON output only
            if (result.error && !result.markdown) {
                // Error with no content - return error in JSON
                return {
                    content: [
                        {
                            type: 'text',
                            text: JSON.stringify(
                                {
                                    markdown: '',
                                    title: undefined,
                                    links: [],
                                    url: args.url,
                                    error: result.error,
                                },
                                null,
                                2
                            ),
                        },
                    ],
                };
            }
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify(jsonData, null, 2),
                    },
                ],
            };
        } else if (outputFormat === 'both') {
            // Both markdown and JSON
            const content: any[] = [];

            // Add markdown content (with error note if applicable)
            if (result.error && result.markdown) {
                content.push({
                    type: 'text',
                    text: `${result.markdown}\n\n---\n*Note: ${result.error}*`,
                });
            } else if (result.markdown) {
                content.push({
                    type: 'text',
                    text: result.markdown,
                });
            }

            // Add JSON content
            content.push({
                type: 'text',
                text: JSON.stringify(jsonData, null, 2),
            });

            return { content };
        } else {
            // Default: markdown output (existing behavior)
            // If there's an error but we still have some content, return it with a note
            if (result.error && result.markdown) {
                return {
                    content: [
                        {
                            type: 'text',
                            text: `${result.markdown}\n\n---\n*Note: ${result.error}*`,
                        },
                    ],
                };
            }

            // If there's an error and no content, throw it
            if (result.error && !result.markdown) {
                throw new Error(result.error);
            }

            return {
                content: [{ type: 'text', text: result.markdown }],
            };
        }
    } catch (error: any) {
        logger.error('Error fetching content:', error.message);
        logger.debug('Error stack:', error.stack);
        logger.debug('Error details:', {
            name: error.name,
            code: error.code,
            ...error,
        });

        // Re-throw with more context
        throw new Error(
            `Failed to fetch content: ${error instanceof Error ? error.message : 'Unknown error'}`
        );
    }
});

// Handle resource listing
server.setRequestHandler(ListResourcesRequestSchema, async () => {
    logger.info('📋 Received ListResources request');
    logger.debug(
        '📋 Returning resources:',
        RESOURCES.map(r => r.uri)
    );
    return {
        resources: RESOURCES,
    };
});

// Handle resource reading
server.setRequestHandler(ReadResourceRequestSchema, async request => {
    logger.debug('Received ReadResource request:', request.params);
    const uri = request.params.uri;

    // Lazy load fs and path modules
    if (!fsPromises) {
        fsPromises = await import('fs/promises');
    }
    if (!pathModule) {
        pathModule = await import('path');
    }

    if (uri === 'read-website-fast://status') {
        try {
            const cacheDir = '.cache';
            const files = await fsPromises.readdir(cacheDir).catch(() => []);

            let totalSize = 0;
            for (const file of files) {
                const stats = await fsPromises
                    .stat(pathModule.join(cacheDir, file))
                    .catch(() => null);
                if (stats) {
                    totalSize += stats.size;
                }
            }

            return {
                contents: [
                    {
                        uri,
                        mimeType: 'application/json',
                        text: JSON.stringify(
                            {
                                cacheSize: totalSize,
                                cacheFiles: files.length,
                                cacheSizeFormatted: `${(totalSize / 1024 / 1024).toFixed(2)} MB`,
                            },
                            null,
                            2
                        ),
                    },
                ],
            };
        } catch (error) {
            return {
                contents: [
                    {
                        uri,
                        mimeType: 'application/json',
                        text: JSON.stringify(
                            {
                                error: 'Failed to get cache status',
                                message:
                                    error instanceof Error
                                        ? error.message
                                        : 'Unknown error',
                            },
                            null,
                            2
                        ),
                    },
                ],
            };
        }
    }

    if (uri === 'read-website-fast://clear-cache') {
        try {
            await fsPromises.rm('.cache', { recursive: true, force: true });

            return {
                contents: [
                    {
                        uri,
                        mimeType: 'application/json',
                        text: JSON.stringify(
                            {
                                status: 'success',
                                message: 'Cache cleared successfully',
                            },
                            null,
                            2
                        ),
                    },
                ],
            };
        } catch (error) {
            return {
                contents: [
                    {
                        uri,
                        mimeType: 'application/json',
                        text: JSON.stringify(
                            {
                                status: 'error',
                                message:
                                    error instanceof Error
                                        ? error.message
                                        : 'Failed to clear cache',
                            },
                            null,
                            2
                        ),
                    },
                ],
            };
        }
    }

    throw new Error(`Unknown resource: ${uri}`);
});

// Start the server
async function runServer() {
    try {
        logger.info('Starting MCP server with HTTP transport...');
        logger.debug('Creating StreamableHTTPServerTransport...');

        const transport = new StreamableHTTPServerTransport({
            sessionIdGenerator: undefined,
        });
        logger.debug('Transport created, connecting to server...');

        // Add transport error handling
        transport.onerror = error => {
            logger.error('Transport Error:', error);
            // Don't exit on transport errors unless it's a connection close
            if (error?.message?.includes('Connection closed')) {
                logger.info('Connection closed by client');
                process.exit(0);
            }
        };

        const port = parseInt(process.env.PORT || '3000', 10);
        const httpServer = createServer((req, res) => {
            transport.handleRequest(req, res).catch((err: unknown) => {
                logger.error('HTTP request error:', err);
            });
        });

        // Handle graceful shutdown
        const cleanup = async (signal: string) => {
            logger.info(`Received ${signal}, shutting down gracefully...`);
            try {
                await server.close();
                await new Promise(resolve => httpServer.close(resolve));
                logger.info('HTTP server closed');
                logger.info('Server closed successfully');
                process.exit(0);
            } catch (error) {
                logger.error('Error during cleanup:', error);
                process.exit(1);
            }
        };

        process.on('SIGINT', () => cleanup('SIGINT'));
        process.on('SIGTERM', () => cleanup('SIGTERM'));

        // Handle unexpected errors
        process.on('uncaughtException', error => {
            logger.error('Uncaught exception:', error.message);
            logger.error('Stack trace:', error.stack);
            logger.debug('Full error object:', error);
            process.exit(1);
        });

        process.on('unhandledRejection', (reason, promise) => {
            logger.error('Unhandled Rejection at:', promise);
            logger.error('Rejection reason:', reason);
            logger.debug('Full rejection details:', { reason, promise });
            // Log but don't exit for promise rejections
        });

        // Log process events
        process.on('exit', code => {
            logger.info(`Process exiting with code: ${code}`);
        });

        process.on('warning', warning => {
            logger.warn('Process warning:', warning.message);
            logger.debug('Warning details:', warning);
        });

        await server.connect(transport);
        httpServer.listen(port, () => {
            logger.info(`HTTP transport listening on port ${port}`);
        });
        logger.info('MCP server connected and running successfully!');
        logger.info('Ready to receive requests');
        logger.info('Available tools:', READ_WEBSITE_TOOL.name);
        logger.info(
            'Available resources:',
            RESOURCES.map(r => r.uri)
        );
        logger.debug('Server details:', {
            name: 'read-website-fast',
            version: '1.0.0',
            pid: process.pid,
            transport: 'HTTP',
            port: port,
        });

        // Log heartbeat every 30 seconds to show server is alive
        setInterval(() => {
            logger.debug('Server heartbeat - still running...');
        }, 30000);
    } catch (error: any) {
        logger.error('Failed to start server:', error.message);
        logger.debug('Startup error details:', error);
        throw error;
    }
}

// Start the server
logger.info('Initializing MCP server...');
runServer().catch(error => {
    logger.error('Fatal server error:', error.message);
    logger.error('Stack trace:', error.stack);
    logger.debug('Full error:', error);
    process.exit(1);
});
