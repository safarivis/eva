import { DSpy, Module, Predict } from 'dspy.ts';
import { OnnxInference } from 'dspy.ts/inference';

interface CodingTask {
    task_id: string;
    description: string;
    status: string;
}

interface CodeSolution {
    task_id: string;
    code: string;
    explanation: string;
}

@Module({
    description: 'A module for handling coding tasks and generating solutions',
})
export class CodingAssistant {
    private dspy: DSpy;
    private inference: OnnxInference;
    private apiBaseUrl: string;

    constructor(apiKey: string, apiBaseUrl: string) {
        this.dspy = new DSpy({
            apiKey,
            temperature: 0.7,
            maxTokens: 500,
        });
        
        this.inference = new OnnxInference({
            modelPath: '/models/coding_assistant.onnx',
        });
        
        this.apiBaseUrl = apiBaseUrl;
    }

    @Predict({
        description: 'Generate initial thoughts about solving a coding task',
        inputFields: ['task'],
        outputFields: ['thoughts'],
    })
    async generateThoughts(task: string): Promise<string> {
        // Use local inference for quick responses
        const thoughts = await this.inference.predict({
            prompt: `Given the coding task: "${task}", what are the key considerations and steps needed?`,
        });
        return thoughts;
    }

    async createTask(description: string): Promise<CodingTask> {
        const response = await fetch(`${this.apiBaseUrl}/tasks/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description }),
        });
        return response.json();
    }

    async solveTask(taskId: string): Promise<CodeSolution> {
        // First, generate local thoughts
        const task = await this.getTask(taskId);
        const thoughts = await this.generateThoughts(task.description);

        // Then, send to server for full solution
        const response = await fetch(`${this.apiBaseUrl}/tasks/${taskId}/solve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ initial_thoughts: thoughts }),
        });
        return response.json();
    }

    private async getTask(taskId: string): Promise<CodingTask> {
        const response = await fetch(`${this.apiBaseUrl}/tasks/${taskId}`);
        return response.json();
    }
}

// Example usage:
// const assistant = new CodingAssistant('your-api-key', 'http://localhost:8000');
// const task = await assistant.createTask('Write a function to calculate fibonacci numbers');
// const solution = await assistant.solveTask(task.task_id);
