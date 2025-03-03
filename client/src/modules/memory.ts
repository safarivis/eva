import { BaseModule, BaseModuleConfig } from './base';
import { Memory } from '../types';
import { VectorDB } from 'dspy.ts/vector';

interface MemorySearchInput {
    query: string;
    limit?: number;
    threshold?: number;
}

interface MemoryStoreInput {
    content: string;
    tags: string[];
    metadata?: Record<string, unknown>;
}

export class MemoryModule extends BaseModule {
    private vectorDB: VectorDB;

    constructor(config: BaseModuleConfig) {
        super({
            ...config,
            signature: {
                inputs: [
                    { name: 'query', type: 'string' },
                    { name: 'limit', type: 'number', optional: true },
                    { name: 'threshold', type: 'number', optional: true }
                ],
                outputs: [
                    { name: 'memories', type: 'array' }
                ]
            }
        });

        this.vectorDB = new VectorDB({
            dimensions: 384, // Adjust based on your embedding model
            metric: 'cosine'
        });
    }

    async search(input: MemorySearchInput): Promise<Memory[]> {
        const { query, limit = 10, threshold = 0.7 } = input;

        try {
            const results = await this.vectorDB.search(query, {
                limit,
                threshold
            });

            const memories = results.map(result => ({
                id: result.id,
                content: result.content,
                tags: result.metadata.tags || [],
                created_at: result.metadata.created_at,
                relevance_score: result.score
            }));

            await this.logMetrics(input, memories);
            return memories;
        } catch (error) {
            console.error('Memory search error:', error);
            throw error;
        }
    }

    async store(input: MemoryStoreInput): Promise<Memory> {
        try {
            const memory = {
                id: crypto.randomUUID(),
                content: input.content,
                tags: input.tags,
                created_at: new Date().toISOString(),
                metadata: input.metadata
            };

            await this.vectorDB.insert(memory.id, memory.content, {
                tags: memory.tags,
                created_at: memory.created_at,
                ...memory.metadata
            });

            await this.logMetrics(input, memory);
            return memory;
        } catch (error) {
            console.error('Memory store error:', error);
            throw error;
        }
    }
}
