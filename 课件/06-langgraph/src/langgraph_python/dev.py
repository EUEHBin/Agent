from langgraph_python.graphs import core_agent_graph
from langgraph_python.graphs.demo import (
    demo_branch_graph,
    demo_dynamic_fanout_graph,
    demo_loop_graph,
    demo_parallel_graph,
    demo_interrupt_graph,
    demo_interrupt_parallel_graph,
    demo_subgraph_interrupt_graph,
)

agent = core_agent_graph.build_graph().compile()
parallel_graph = demo_parallel_graph.build_graph().compile()
branch_graph = demo_branch_graph.build_graph().compile()
loop_graph = demo_loop_graph.build_graph().compile()
interrupt_graph = demo_interrupt_graph.build_graph().compile()
interrupt_parallel_graph = demo_interrupt_parallel_graph.build_graph().compile()
subgraph_interrupt_graph = demo_subgraph_interrupt_graph.build_graph().compile()
dynamic_fanout_graph = demo_dynamic_fanout_graph.build_graph().compile()
