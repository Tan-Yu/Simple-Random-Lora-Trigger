// File: web/js/easyuse_dynamic_lora_stack.js
// EasyUse's EXACT method for dynamic input fields

import { app } from "../../scripts/app.js";

// Main dynamic widgets implementation (based on EasyUse's easyDynamicWidgets.js)
function createDynamicWidget(node, widget_name, type, value, options = {}) {
    // Create widget dynamically
    const widget = node.addWidget(type, widget_name, value, function(v) {
        node.onWidgetChanged?.(widget_name, v);
    }, options);
    return widget;
}

function removeDynamicWidget(node, widget_name) {
    // Remove widget by name
    const index = node.widgets?.findIndex(w => w.name === widget_name);
    if (index !== undefined && index >= 0) {
        node.widgets.splice(index, 1);
    }
}

function updateDynamicInputs(node, num_loras) {
    const MAX_LORA_NUM = 10;
    
    // Get current widget names
    const currentWidgets = new Set((node.widgets || []).map(w => w.name));
    
    // Define required widgets for each slot
    const getSlotWidgets = (i) => [
        `lora_${i}_name`,
        `lora_${i}_strength`, 
        `lora_${i}_model_strength`,
        `lora_${i}_clip_strength`
    ];
    
    // Remove widgets for slots > num_loras
    for (let i = num_loras + 1; i <= MAX_LORA_NUM; i++) {
        getSlotWidgets(i).forEach(widget_name => {
            if (currentWidgets.has(widget_name)) {
                removeDynamicWidget(node, widget_name);
            }
        });
    }
    
    // Add widgets for slots <= num_loras that don't exist
    for (let i = 1; i <= num_loras; i++) {
        const slotWidgets = getSlotWidgets(i);
        
        slotWidgets.forEach(widget_name => {
            if (!currentWidgets.has(widget_name)) {
                // Determine widget type and options based on name
                if (widget_name.includes('_name')) {
                    const loras = ["None", ...app.ui.settings.getSettingValue("Comfy.LoraList", [])];
                    createDynamicWidget(node, widget_name, "combo", "None", {values: loras});
                } else {
                    // Strength widgets
                    createDynamicWidget(node, widget_name, "number", 1.0, {
                        min: -10.0,
                        max: 10.0,
                        step: 0.01
                    });
                }
            }
        });
    }
    
    // Force node resize
    node.setSize([Math.max(300, node.size[0]), node.computeSize()[1]]);
    node.setDirtyCanvas(true, true);
}

// Register the extension
app.registerExtension({
    name: "EasyUseDynamicLoraStack",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EasyUse Dynamic LoRA Stack") {
            
            // Store original onNodeCreated
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = function () {
                // Call original function
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }
                
                // Set up dynamic behavior
                this.setupDynamicLoraInputs();
            };
            
            nodeType.prototype.setupDynamicLoraInputs = function () {
                // Find the num_loras widget
                const numLorasWidget = this.widgets?.find(w => w.name === "num_loras");
                if (!numLorasWidget) return;
                
                // Store original callback
                const originalCallback = numLorasWidget.callback;
                
                // Set up new callback for num_loras changes
                numLorasWidget.callback = (value) => {
                    // Call original callback if it exists
                    if (originalCallback) {
                        originalCallback.call(this, value);
                    }
                    
                    // Update dynamic inputs based on new value
                    updateDynamicInputs(this, value);
                };
                
                // Initial setup - trigger once to set up initial widgets
                setTimeout(() => {
                    updateDynamicInputs(this, numLorasWidget.value);
                }, 100);
            };
            
            // Handle widget changes for mode switching
            const onWidgetChanged = nodeType.prototype.onWidgetChanged;
            nodeType.prototype.onWidgetChanged = function(name, value, old_value) {
                if (onWidgetChanged) {
                    onWidgetChanged.apply(this, arguments);
                }
                
                if (name === "mode") {
                    // Mode changed - update widget visibility
                    const modeValue = value;
                    const widgets = this.widgets || [];
                    
                    widgets.forEach(widget => {
                        if (widget.name.includes('_model_strength') || widget.name.includes('_clip_strength')) {
                            // Show these only in advanced mode
                            widget.type = modeValue === "advanced" ? widget.type : "hidden";
                        } else if (widget.name.includes('_strength') && !widget.name.includes('_model_') && !widget.name.includes('_clip_')) {
                            // Show simple strength only in simple mode
                            widget.type = modeValue === "simple" ? widget.type : "hidden";
                        }
                    });
                    
                    this.setDirtyCanvas(true, true);
                }
            };
        }
    }
});

// Alternative simpler implementation using CSS (backup method)
app.registerExtension({
    name: "EasyUseDynamicLoraStack.CSS",
    
    async setup() {
        // Add CSS for hiding inactive widgets
        const style = document.createElement('style');
        style.textContent = `
            .comfy-widget.dynamic-lora-hidden {
                display: none !important;
            }
            .comfy-widget.dynamic-lora-inactive {
                opacity: 0.3;
                pointer-events: none;
            }
        `;
        document.head.appendChild(style);
    },
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EasyUse Dynamic LoRA Stack") {
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }
                
                // Setup CSS-based hiding
                this.setupCSSHiding();
            };
            
            nodeType.prototype.setupCSSHiding = function() {
                const updateVisibility = () => {
                    const numLorasWidget = this.widgets?.find(w => w.name === "num_loras");
                    if (!numLorasWidget) return;
                    
                    const numLoras = numLorasWidget.value;
                    const MAX_LORA_NUM = 10;
                    
                    // Update visibility for each slot
                    for (let i = 1; i <= MAX_LORA_NUM; i++) {
                        const shouldShow = i <= numLoras;
                        const slotWidgets = [
                            `lora_${i}_name`,
                            `lora_${i}_strength`,
                            `lora_${i}_model_strength`, 
                            `lora_${i}_clip_strength`
                        ];
                        
                        slotWidgets.forEach(widgetName => {
                            const widget = this.widgets?.find(w => w.name === widgetName);
                            if (widget && widget.element) {
                                if (shouldShow) {
                                    widget.element.classList.remove('dynamic-lora-hidden');
                                } else {
                                    widget.element.classList.add('dynamic-lora-hidden');
                                }
                            }
                        });
                    }
                };
                
                // Set up callback
                const numLorasWidget = this.widgets?.find(w => w.name === "num_loras");
                if (numLorasWidget) {
                    const originalCallback = numLorasWidget.callback;
                    numLorasWidget.callback = (value) => {
                        if (originalCallback) {
                            originalCallback.call(this, value);
                        }
                        setTimeout(updateVisibility, 10);
                    };
                }
                
                // Initial visibility update
                setTimeout(updateVisibility, 100);
            };
        }
    }
});