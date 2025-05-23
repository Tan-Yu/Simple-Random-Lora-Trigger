import { app } from "../../../../scripts/app.js";

// Utility functions
function findWidgetByName(node, name) {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
}

function toggleWidget(node, widget, show = false) {
    if (!widget) return;
    
    widget.type = show ? widget.origType : "hidden";
    if (widget.origType == null) {
        widget.origType = widget.type;
    }
    
    if (widget.linkedWidgets) {
        for (let i in widget.linkedWidgets) {
            toggleWidget(node, widget.linkedWidgets[i], show);
        }
    }
    
    const stack = [widget];
    while (stack.length) {
        const w = stack.pop();
        if (w.linkedWidgets) {
            stack.push(...w.linkedWidgets);
        }
        if (w.type === "hidden") {
            w.computeSize = () => [0, -4]; // -4 is the margin
        } else {
            delete w.computeSize;
        }
    }
}

function updateNodeHeight(node) {
    requestAnimationFrame(() => {
        const sz = node.computeSize();
        if (sz[0] < node.size[0]) {
            sz[0] = node.size[0];
        }
        if (sz[1] < node.size[1]) {
            sz[1] = node.size[1];
        }
        node.onResize?.(sz);
        app.graph.setDirtyCanvas(true, false);
    });
}

function randomLoraChooserWidgetLogic(node, widget) {
    if (widget.name === 'num_loras') {
        const number_to_show = widget.value;
        const max_loras = 20;
        
        // Show widgets for active LoRAs
        for (let i = 1; i <= number_to_show; i++) {
            const nameWidget = findWidgetByName(node, `lora_${i}_name`);
            const triggerWidget = findWidgetByName(node, `lora_${i}_trigger`);
            
            toggleWidget(node, nameWidget, true);
            toggleWidget(node, triggerWidget, true);
            
            // Handle different weight widgets based on node type
            if (node.comfyClass === 'RandomLoraChooser') {
                const weightWidget = findWidgetByName(node, `lora_${i}_weight`);
                toggleWidget(node, weightWidget, true);
            } else if (node.comfyClass === 'RandomLoraChooserAdvanced') {
                const modelWeightWidget = findWidgetByName(node, `lora_${i}_model_weight`);
                const clipWeightWidget = findWidgetByName(node, `lora_${i}_clip_weight`);
                toggleWidget(node, modelWeightWidget, true);
                toggleWidget(node, clipWeightWidget, true);
            }
        }
        
        // Hide widgets for inactive LoRAs
        for (let i = number_to_show + 1; i <= max_loras; i++) {
            const nameWidget = findWidgetByName(node, `lora_${i}_name`);
            const triggerWidget = findWidgetByName(node, `lora_${i}_trigger`);
            
            toggleWidget(node, nameWidget, false);
            toggleWidget(node, triggerWidget, false);
            
            // Handle different weight widgets based on node type
            if (node.comfyClass === 'RandomLoraChooser') {
                const weightWidget = findWidgetByName(node, `lora_${i}_weight`);
                toggleWidget(node, weightWidget, false);
            } else if (node.comfyClass === 'RandomLoraChooserAdvanced') {
                const modelWeightWidget = findWidgetByName(node, `lora_${i}_model_weight`);
                const clipWeightWidget = findWidgetByName(node, `lora_${i}_clip_weight`);
                toggleWidget(node, modelWeightWidget, false);
                toggleWidget(node, clipWeightWidget, false);
            }
        }
        
        updateNodeHeight(node);
    }
    
    if (widget.name === 'randomize_seed') {
        const seedWidget = findWidgetByName(node, 'seed');
        if (widget.value) {
            // When randomize is enabled, optionally hide/disable seed input
            // toggleWidget(node, seedWidget, false);
        } else {
            toggleWidget(node, seedWidget, true);
        }
    }
}

function setupDynamicWidgets(node) {
    if (!node.widgets) return;
    
    for (const widget of node.widgets) {
        if (['num_loras', 'randomize_seed'].includes(widget.name)) {
            // Initial setup
            randomLoraChooserWidgetLogic(node, widget);
            
            // Store original value
            let widgetValue = widget.value;
            
            // Define getter and setter for dynamic behavior
            Object.defineProperty(widget, 'value', {
                get() {
                    return widgetValue;
                },
                set(newVal) {
                    if (newVal !== widgetValue) {
                        widgetValue = newVal;
                        randomLoraChooserWidgetLogic(node, widget);
                    }
                }
            });
        }
    }
}

// Register the extension
app.registerExtension({
    name: "RandomLoraChooser.DynamicWidgets",
    
    nodeCreated(node) {
        if (node.comfyClass === "RandomLoraChooser" || node.comfyClass === "RandomLoraChooserAdvanced") {
            setupDynamicWidgets(node);
        }
    },
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "RandomLoraChooser" || nodeData.name === "RandomLoraChooserAdvanced") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = async function() {
                onNodeCreated?.apply(this, arguments);
                
                // Add random seed button
                const randomSeedButton = this.addWidget("button", "🎲 New Random Seed", null, () => {
                    const seedWidget = findWidgetByName(this, 'seed');
                    const randomizeWidget = findWidgetByName(this, 'randomize_seed');
                    
                    if (seedWidget) {
                        seedWidget.value = Math.floor(Math.random() * 0xffffffffffffffff);
                    }
                    
                    // Temporarily disable randomize to use the specific seed
                    if (randomizeWidget) {
                        randomizeWidget.value = false;
                    }
                }, { serialize: false });
                
                // Add choose random LoRA button
                const chooseButton = this.addWidget("button", "🎯 Choose Random LoRA", null, () => {
                    // This will trigger the node execution
                    app.queuePrompt(0, 1);
                }, { serialize: false });
                
                // Setup initial widget visibility
                setTimeout(() => {
                    setupDynamicWidgets(this);
                }, 100);
            };
        }
    }
});