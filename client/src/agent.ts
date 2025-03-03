import { Pipeline, BootstrapFewShot, exactMatchMetric } from 'dspy.ts';
import { CodeGenModule } from './modules/codeGen';
import { MemoryModule } from './modules/memory';
import { CodingTask, CodeSolution, AgentConfig } from './types';

@Module({
    description: 'A module for handling coding tasks and generating solutions',
})
export class CodingAssistant {
    private codeGen: CodeGenModule;
    private memory: MemoryModule;
    private pipeline: Pipeline;
    private apiBaseUrl: string;

    constructor(config: AgentConfig) {
        // Initialize modules
        this.codeGen = new CodeGenModule({
            name: 'CodeGenerator',
            strategy: 'ChainOfThought',
            optimization: {
                metric: 'exactMatch',
                method: 'BootstrapFewShot'
            }
        });

        this.memory = new MemoryModule({
            name: 'MemoryManager',
            strategy: 'ReAct'
        });

        // Create pipeline
        this.pipeline = new Pipeline([
            this.memory,  // First check memory for similar solutions
            this.codeGen  // Then generate new solution if needed
        ]);

        this.apiBaseUrl = config.apiBaseUrl;
    }

    @Predict({
        description: 'Create a new coding task',
        inputFields: ['description'],
        outputFields: ['task'],
    })
    async createTask(description: string): Promise<CodingTask> {
        const task: CodingTask = {
            task_id: crypto.randomUUID(),
            description,
            status: 'pending',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };

        // Store task in memory for future reference
        await this.memory.store({
            content: description,
            tags: ['task', 'pending']
        });

        return task;
    }

    @Predict({
        description: 'Solve a coding task',
        inputFields: ['taskId'],
        outputFields: ['solution'],
    })
    async solveTask(taskId: string): Promise<CodeSolution> {
        try {
            // Get task details
            const task = await this.getTask(taskId);
            
            // Search memory for similar tasks
            const memories = await this.memory.search({
                query: task.description,
                limit: 5,
                threshold: 0.8
            });

            // Generate solution using pipeline
            const solution = await this.pipeline.run({
                description: task.description,
                context: memories.map(m => m.content),
                language: this.detectLanguage(task.description)
            });

            // Format and store solution
            const codeSolution: CodeSolution = {
                task_id: taskId,
                code: solution.code,
                explanation: solution.explanation,
                language: this.detectLanguage(solution.code),
                created_at: new Date().toISOString()
            };

            // Store solution in memory
            await this.memory.store({
                content: solution.code,
                tags: ['solution', codeSolution.language],
                metadata: {
                    task_id: taskId,
                    confidence: solution.confidence
                }
            });

            return codeSolution;
        } catch (error) {
            console.error('Error solving task:', error);
            throw error;
        }
    }

    private async getTask(taskId: string): Promise<CodingTask> {
        const response = await fetch(`${this.apiBaseUrl}/tasks/${taskId}`);
        return response.json();
    }

    private detectLanguage(text: string): string {
        // Simple language detection based on common patterns
        if (text.includes('def ') || text.includes('import ')) return 'python';
        if (text.includes('function ') || text.includes('const ')) return 'javascript';
        if (text.includes('class ') && text.includes('{')) return 'typescript';
        return 'unknown';
    }

    // Optional: Add methods to optimize the pipeline
    async optimizePipeline(examples: Array<{ input: string; output: string }>) {
        const optimizer = new BootstrapFewShot(exactMatchMetric);
        this.pipeline = await optimizer.compile(this.pipeline, examples);
    }
}
