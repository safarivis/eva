export interface CodingTask {
    task_id: string;
    description: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    created_at: string;
    updated_at: string;
}

export interface CodeSolution {
    task_id: string;
    code: string;
    explanation: string;
    language: string;
    created_at: string;
}

export interface Memory {
    id: string;
    content: string;
    tags: string[];
    created_at: string;
    relevance_score?: number;
}

export interface MCPTool {
    name: string;
    description: string;
    parameters: Record<string, unknown>;
}

export interface AgentConfig {
    apiKey: string;
    apiBaseUrl: string;
    temperature?: number;
    maxTokens?: number;
    modelName?: string;
}
