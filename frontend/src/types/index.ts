export interface App {
  id: string;
  name: string;
  mode: string;
  icon: string;
  icon_type: string;
  icon_background: string;
  description: string;
  use_icon_as_answer_icon: boolean;
}

export interface EnvironmentVariable {
  name: string;
  value: string;
  value_type: 'string' | 'secret';
}

export interface WorkflowNode {
  id: string;
  type: string;
  data: any;
  position: {
    x: number;
    y: number;
  };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  source_handle: string;
  target_handle: string;
}

export interface Workflow {
  id: string;
  app_id: string;
  version: string;
  graph: {
    nodes: WorkflowNode[];
    edges: WorkflowEdge[];
  };
  features: any;
  environment_variables: EnvironmentVariable[];
} 