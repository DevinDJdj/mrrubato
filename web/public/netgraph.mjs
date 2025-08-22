/**
 * Class to manage and visualize network graphs using vis.js
 */
export class NetworkGraph {
    /**
     * Creates a new NetworkGraph instance
     * @param {HTMLElement} container - DOM element to render the graph
     * @param {Object} options - Visualization options
     */
    constructor(container, options = {}) {
        this.container = container;
        this.nodes = new vis.DataSet([]);
        this.edges = new vis.DataSet([]);
        
        // Default options merged with provided options
        this.options = {
            nodes: {
                shape: 'dot',
                size: 16,
                font: {
                    size: 12,
                    color: '#000000'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                shadow: true,
                smooth: {
                    type: 'continuous'
                }
            },
            physics: {
                stabilization: false,
                barnesHut: {
                    gravitationalConstant: -80000,
                    springConstant: 0.001,
                    springLength: 200
                }
            },
            interaction: {
                navigationButtons: true,
                keyboard: true
            },
            ...options
        };

        this.network = new vis.Network(
            container, 
            { nodes: this.nodes, edges: this.edges },
            this.options
        );

        // Bind event handlers
        this.network.on('selectNode', this.handleNodeSelect.bind(this));
        this.network.on('selectEdge', this.handleEdgeSelect.bind(this));
        
//        this.selectedCallback = null;
    }

    /**
     * Add a node to the graph
     * @param {Object} nodeData - Node data including id and label
     */
    addNode(nodeData) {
        try {
            this.nodes.add({
                id: nodeData.id,
                label: nodeData.label,
                title: nodeData.title || nodeData.label,
                color: nodeData.color || '#97c2fc',
                ...nodeData
            });
        } catch (error) {
            console.error('Error adding node:', error);
        }
    }

    /**
     * Add multiple nodes to the graph
     * @param {Array} nodesData - Array of node data objects
     */
    addNodes(nodesData) {
        try {
            this.nodes.add(nodesData.map(node => ({
                id: node.id,
                label: node.label,
                title: node.title || node.label,
                color: node.color || '#97c2fc',
                ...node
            })));
        } catch (error) {
            console.error('Error adding nodes:', error);
        }
    }

    /**
     * Add an edge between nodes
     * @param {Object} edgeData - Edge data including from and to node ids
     */
    addEdge(edgeData) {
        try {
            this.edges.add({
                id: edgeData.id || `${edgeData.from}-${edgeData.to}`,
                arrows: edgeData.arrows || 'to',
                width: edgeData.width || 2,
                ...edgeData
            });
        } catch (error) {
            console.error('Error adding edge:', error);
        }
    }

    /**
     * Add multiple edges to the graph
     * @param {Array} edgesData - Array of edge data objects
     */
    addEdges(edgesData) {
        try {
            this.edges.add(edgesData.map(edge => ({
                id: edge.id || `${edge.from}-${edge.to}`,
                arrows: edge.arrows || 'to',
                width: edge.width || 2,
                ...edge
            })));
        } catch (error) {
            console.error('Error adding edges:', error);
        }
    }

    /**
     * Remove a node and its connected edges
     * @param {string|number} nodeId - ID of the node to remove
     */
    removeNode(nodeId) {
        try {
            this.nodes.remove(nodeId);
        } catch (error) {
            console.error('Error removing node:', error);
        }
    }

    /**
     * Remove an edge from the graph
     * @param {string} edgeId - ID of the edge to remove
     */
    removeEdge(edgeId) {
        try {
            this.edges.remove(edgeId);
        } catch (error) {
            console.error('Error removing edge:', error);
        }
    }

    /**
     * Update node properties
     * @param {string|number} nodeId - ID of the node to update
     * @param {Object} updateData - Properties to update
     */
    updateNode(nodeId, updateData) {
        try {
            this.nodes.update({
                id: nodeId,
                ...updateData
            });
        } catch (error) {
            console.error('Error updating node:', error);
        }
    }

    /**
     * Update edge properties
     * @param {string} edgeId - ID of the edge to update
     * @param {Object} updateData - Properties to update
     */
    updateEdge(edgeId, updateData) {
        try {
            this.edges.update({
                id: edgeId,
                ...updateData
            });
        } catch (error) {
            console.error('Error updating edge:', error);
        }
    }

    /**
     * Set callback for node/edge selection
     * @param {Function} callback - Function to call on selection
     */
    setSelectionCallback(callback) {
        this.selectedCallback = callback;
    }

    /**
     * Handle node selection event
     * @param {Object} params - Selection event parameters
     * @private
     */
    handleNodeSelect(params) {
        if (this.selectedCallback) {
            this.selectedCallback({
                type: 'node',
                selected: params.nodes,
                data: this.nodes.get(params.nodes)
            });
        }
    }

    /**
     * Handle edge selection event
     * @param {Object} params - Selection event parameters
     * @private
     */
    handleEdgeSelect(params) {
        if (this.selectedCallback) {
            this.selectedCallback({
                type: 'edge',
                selected: params.edges,
                data: this.edges.get(params.edges)
            });
        }
    }

    /**
     * Import graph from DOT language string
     * @param {string} dotString - Graph definition in DOT language
     */
    importDot(dotString) {
        try {
            let parsedData = vis.parseDOTNetwork(dotString);

            let data = {
              nodes: parsedData.nodes,
              edges: parsedData.edges
            }
            
            let options = parsedData.options;
            this.options = options;
            this.options.interaction = {
                navigationButtons: true,
                keyboard: true //not sure if we want this.  
            };
            //graph settings.  
            this.options.physics = {
                enabled: true,
                barnesHut: {
                    gravitationalConstant: -5000 // This is the default * 25.
                  },
                stabilization: {
                  enabled: true,
                  iterations: 10
                }
              }
    
            // create a network
            this.network = new vis.Network(this.container, data, options);

            this.network.on('selectNode', this.handleNodeSelect.bind(this));
            this.network.on('selectEdge', this.handleEdgeSelect.bind(this));
            
            this.network.on('click', function (properties) {
                var clickedNodes = properties.nodes;
                var clickedEdges = properties.edges;
        
                if (clickedNodes.length > 0) {
                    // A node was clicked
                    var nodeId = clickedNodes[0];
//                    var nodeData = nodes.get(nodeId); // Access node data from your nodes DataSet
                    console.log('Clicked node:', nodeId);
                    // Perform actions based on the clicked node
                } else if (clickedEdges.length > 0) {
                    // An edge was clicked
                    var edgeId = clickedEdges[0];
//                    var edgeData = edges.get(edgeId); // Access edge data from your edges DataSet
                    console.log('Clicked edge:', edgeId);
                    // Perform actions based on the clicked edge
                } else {
                    // Background was clicked
                    console.log('Clicked background');
                    // Perform actions for background clicks
                }
            });
            
            this.selectedCallback = null; //callback for selection.  

        } catch (error) {
            console.error('Error importing DOT:', error);
        }
    }

    /**
     * Focus on a specific node
     * @param {string|number} nodeId - ID of node to focus on
     * @param {Object} options - Animation options
     */
    focusNode(nodeId, options = {}) {
        try {
            this.network.focus(nodeId, {
                scale: 1.0,
                animation: true,
                ...options
            });
        } catch (error) {
            console.error('Error focusing node:', error);
        }
    }

    /**
     * Get the current graph data
     * @returns {Object} Current nodes and edges
     */
    getData() {
        return {
            nodes: this.nodes.get(),
            edges: this.edges.get()
        };
    }

    /**
     * Clear all nodes and edges from the graph
     */
    clear() {
        this.nodes.clear();
        this.edges.clear();
    }

    /**
     * Fit the graph view to show all nodes
     * @param {Object} options - Animation options
     */
    fit(options = {}) {
        this.network.fit({
            animation: true,
            ...options
        });
    }

    simpleGraph(graphstr = `
            digraph {
                A -> B;
                B -> C;
                C -> A;
            }
        `){
        /*            
        this.addNode({
            id: 1,
            label: 'Node 1',
            color: '#ff0000'
        });
        this.addEdge({
            from: 1,
            to: 2,
            label: 'connects to'
        });
        */
        this.setSelectionCallback(({ type, selected, data }) => {
            console.log(`Selected ${type}:`, data);
        });
        this.importDot(graphstr);
    }
}

