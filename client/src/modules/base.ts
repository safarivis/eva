import { PredictModule, ModuleConfig } from 'dspy.ts';

export interface BaseModuleConfig extends ModuleConfig {
    name: string;
    strategy?: 'ReAct' | 'ChainOfThought';
    optimization?: {
        metric: string;
        method: 'BootstrapFewShot';
    };
}

export abstract class BaseModule extends PredictModule {
    protected config: BaseModuleConfig;

    constructor(config: BaseModuleConfig) {
        super({
            name: config.name,
            strategy: config.strategy || 'ReAct',
            optimization: config.optimization
        });
        this.config = config;
    }

    protected async validateOutput<T>(output: T): Promise<T> {
        // Add validation logic here
        return output;
    }

    protected async logMetrics(input: unknown, output: unknown): Promise<void> {
        // Add metrics logging here
        console.log(`Module ${this.config.name} metrics:`, {
            input,
            output,
            timestamp: new Date().toISOString()
        });
    }
}
