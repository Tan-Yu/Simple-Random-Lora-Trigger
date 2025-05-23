import { app } from "../../scripts/app.js";

// Helper function to get lora list from ComfyUI
function getLoraList() {
    try {
        // Try to get lora list from various sources
        if (window.ComfyApi?.objectInfo) {
            // Method 1: From object info
            const objectInfo = window.ComfyApi.objectInfo;
            for (let nodeType in objectInfo) {
                const nodeInfo = objectInfo[nodeType];
                if (nodeInfo.input && nodeInfo.input.required) {
                    for (let inputName in nodeInfo.input.required) {
                        const inputInfo = nodeInfo.input.required[inputName];
                        if (Array.isArray(inputInfo) && inputInfo[0] && Array.isArray(inputInfo[0])) {
                            const options = inputInfo[0];
                            if (options.some(opt => opt.includes('.safetensors') || opt.includes('.ckpt'))) {
                                return ["None", ...options.filter(opt => opt !== "None")];
                            }
                        }
                    }
                }
            }
        }
        
        // Method 2: Fallback to basic list
        return ["None", "lora1.safetensors", "lora2.safetensors"];
    } catch (e) {
        console.warn("Could not get lora list:", e);
        return ["None"];
    }
}

// Main dynamic widgets implementation
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
                const MAX_LORA_NUM = 10;
                
                // Find the num_loras widget
                const numLorasWidget = this.widgets?.find(w => w.name === "num_loras");
                if (!numLorasWidget) return;
                
                // Function to update widget visibility
                const updateWidgetVisibility = () => {
                    const numLoras = numLorasWidget.value;
                    const mode = this.widgets?.find(w => w.name === "mode")?.value || "simple";
                    
                    // Get all widgets
                    const widgets = this.widgets || [];
                    
                    // Update visibility for each slot
                    for (let i = 1; i <= MAX_LORA_NUM; i++) {
                        const shouldShow = i <= numLoras;
                        
                        // Find widgets for this slot
                        const nameWidget = widgets.find(w => w.name === `lora_${i}_name`);
                        const strengthWidget = widgets.find(w => w.name === `lora_${i}_strength`);
                        const modelStrWidget = widgets.find(w => w.name === `lora_${i}_model_strength`);
                        const clipStrWidget = widgets.find(w => w.name === `lora_${i}_clip_strength`);
                        
                        // Update visibility
                        if (nameWidget) {
                            nameWidget.type = shouldShow ? nameWidget.type : "hidden";
                            if (nameWidget.element) {
                                nameWidget.element.style.display = shouldShow ? "" : "none";
                            }
                        }
                        
                        // Show strength widgets based on mode
                        if (strengthWidget) {
                            const showStrength = shouldShow && mode === "simple";
                            strengthWidget.type = showStrength ? strengthWidget.type : "hidden";
                            if (strengthWidget.element) {
                                strengthWidget.element.style.display = showStrength ? "" : "none";
                            }
                        }
                        
                        if (modelStrWidget) {
                            const showAdvanced = shouldShow && mode === "advanced";
                            modelStrWidget.type = showAdvanced ? modelStrWidget.type : "hidden";
                            if (modelStrWidget.element) {
                                modelStrWidget.element.style.display = showAdvanced ? "" : "none";
                            }
                        }
                        
                        if (clipStrWidget) {
                            const showAdvanced = shouldShow && mode === "advanced";
                            clipStrWidget.type = showAdvanced ? clipStrWidget.type : "hidden";
                            if (clipStrWidget.element) {
                                clipStrWidget.element.style.display = showAdvanced ? "" : "none";
                            }
                        }
                    }
                    
                    // Force node to recalculate size
                    this.setDirtyCanvas(true, true);
                    if (this.graph && this.graph.canvas) {
                        this.graph.canvas.draw(true, true);
                    }
                };
                
                // Set up callback for num_loras changes
                const originalNumLorasCallback = numLorasWidget.callback;
                numLorasWidget.callback = (value) => {
                    if (originalNumLorasCallback) {
                        originalNumLorasCallback.call(this, value);
                    }
                    setTimeout(updateWidgetVisibility, 10);
                };
                
                // Set up callback for mode changes
                const modeWidget = this.widgets?.find(w => w.name === "mode");
                if (modeWidget) {
                    const originalModeCallback = modeWidget.callback;
                    modeWidget.callback = (value) => {
                        if (originalModeCallback) {
                            originalModeCallback.call(this, value);
                        }
                        setTimeout(updateWidgetVisibility, 10);
                    };
                }
                
                // Initial visibility update
                setTimeout(updateWidgetVisibility, 100);
            };
        }
    }
});

// Alternative CSS-based implementation (more reliable)
app.registerExtension({
    name: "EasyUseDynamicLoraStack.CSS",
    
    async setup() {
        // Add CSS for hiding inactive widgets
        const style = document.createElement('style');
        style.textContent = `
            .comfy-widget.dynamic-lora-hidden {
                display: none !important;
                height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            
            .litegraph .node .widget.dynamic-lora-hidden {
                display: none !important;
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
                
                this.setupCSSBasedHiding();
            };
            
            nodeType.prototype.setupCSSBasedHiding = function() {
                const MAX_LORA_NUM = 10;
                
                const updateVisibility = () => {
                    const numLorasWidget = this.widgets?.find(w => w.name === "num_loras");
                    const modeWidget = this.widgets?.find(w => w.name === "mode");
                    
                    if (!numLorasWidget) return;
                    
                    const numLoras = numLorasWidget.value;
                    const mode = modeWidget?.value || "simple";
                    
                    // Update visibility for each slot
                    for (let i = 1; i <= MAX_LORA_NUM; i++) {
                        const shouldShow = i <= numLoras;
                        
                        const widgetNames = [
                            `lora_${i}_name`,
                            `lora_${i}_strength`,
                            `lora_${i}_model_strength`,
                            `lora_${i}_clip_strength`
                        ];
                        
                        widgetNames.forEach(widgetName => {
                            const widget = this.widgets?.find(w => w.name === widgetName);
                            if (widget) {
                                // Determine if this specific widget should be shown
                                let showWidget = shouldShow;
                                
                                if (widgetName.includes('_strength') && !widgetName.includes('_model_') && !widgetName.includes('_clip_')) {
                                    // Simple strength - only show in simple mode
                                    showWidget = shouldShow && mode === "simple";
                                } else if (widgetName.includes('_model_strength') || widgetName.includes('_clip_strength')) {
                                    // Advanced strength - only show in advanced mode
                                    showWidget = shouldShow && mode === "advanced";
                                }
                                
                                if (widget.element) {
                                    if (showWidget) {
                                        widget.element.classList.remove('dynamic-lora-hidden');
                                        widget.element.style.display = '';
                                    } else {
                                        widget.element.classList.add('dynamic-lora-hidden');
                                        widget.element.style.display = 'none';
                                    }
                                }
                                
                                // Also update the widget's type for ComfyUI's internal handling
                                if (showWidget) {
                                    if (widget.type === "hidden") {
                                        widget.type = widgetName.includes('_name') ? "combo" : "number";
                                    }
                                } else {
                                    widget.type = "hidden";
                                }
                            }
                        });
                    }
                    
                    // Force node size recalculation
                    this.size = this.computeSize();
                    this.setDirtyCanvas(true, true);
                };
                
                // Set up callbacks
                const numLorasWidget = this.widgets?.find(w => w.name === "num_loras");
                const modeWidget = this.widgets?.find(w => w.name === "mode");
                
                if (numLorasWidget) {
                    const originalCallback = numLorasWidget.callback;
                    numLorasWidget.callback = (value) => {
                        if (originalCallback) {
                            originalCallback.call(this, value);
                        }
                        setTimeout(updateVisibility, 10);
                    };
                }
                
                if (modeWidget) {
                    const originalCallback = modeWidget.callback;
                    modeWidget.callback = (value) => {
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