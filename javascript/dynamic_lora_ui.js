import { app } from "../../scripts/app.js";

// Configuration
const NODE_CONFIGS = {
    "SimpleRandomLoraChooser": {
        maxSlots: 8,
        paramName: "num_loras",
        slotInputs: [
            { prefix: "lora_", suffix: "" },
            { prefix: "triggers_", suffix: "" }
        ]
    },
    "DynamicRandomLoraChooser": {
        maxSlots: 10,
        paramName: "num_loras",
        slotPrefix: "lora_",
        slotInputs: ["_name", "_min_strength", "_max_strength", "_weight", "_trigger_words"]
    }
};

function hideWidget(widget) {
    if (!widget) return;
    widget.origType = widget.origType || widget.type;
    widget.origComputeSize = widget.origComputeSize || widget.computeSize;
    widget.type = "hidden";
    widget.computeSize = () => [0, -4];
}

function showWidget(widget) {
    if (!widget) return;
    if (widget.origType) widget.type = widget.origType;
    if (widget.origComputeSize) widget.computeSize = widget.origComputeSize;
    delete widget.origType;
    delete widget.origComputeSize;
}

function updateNodeInputsVisibility(node, config) {
    const widgets = node.widgets;
    if (!widgets || widgets.length === 0) {
        return setTimeout(() => updateNodeInputsVisibility(node, config), 50);
    }

    const numWidget = widgets.find(w => w.name === config.paramName);
    const numLoras = parseInt(numWidget?.value ?? 1) || 1;

    if (config.slotInputs[0].prefix) {
        for (let i = 1; i <= config.maxSlots; i++) {
            const show = i <= numLoras;
            for (const input of config.slotInputs) {
                const name = `${input.prefix}${i}${input.suffix}`;
                const w = widgets.find(w => w.name === name);
                show ? showWidget(w) : hideWidget(w);
            }
        }
    } else {
        for (let i = 1; i <= config.maxSlots; i++) {
            const show = i <= numLoras;
            for (const suffix of config.slotInputs) {
                const name = `${config.slotPrefix}${i}${suffix}`;
                const w = widgets.find(w => w.name === name);
                show ? showWidget(w) : hideWidget(w);
            }
        }
    }

    requestAnimationFrame(() => {
        node.setDirtyCanvas(true, true);
        if (node.onResize) node.onResize(node.size);
    });
}

function setupDynamicNode(nodeType, nodeData) {
    const config = NODE_CONFIGS[nodeData.name];
    if (!config) return;

    const originalCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
        const result = originalCreated?.apply(this, arguments);
        setTimeout(() => updateNodeInputsVisibility(this, config), 100);
        return result;
    };

    const originalConfigure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function (info) {
        const result = originalConfigure?.apply(this, arguments);
        setTimeout(() => updateNodeInputsVisibility(this, config), 100);
        return result;
    };

    const originalChanged = nodeType.prototype.onWidgetChanged;
    nodeType.prototype.onWidgetChanged = function (name, value, oldValue, widget) {
        const result = originalChanged?.apply(this, arguments);
        if (name === config.paramName) {
            updateNodeInputsVisibility(this, config);
        }
        return result;
    };

    const originalMenu = nodeType.prototype.getExtraMenuOptions;
    nodeType.prototype.getExtraMenuOptions = function (_, options) {
        const result = originalMenu?.apply(this, arguments) || [];
        options.push({
            content: "🔄 Refresh LoRA UI",
            callback: () => updateNodeInputsVisibility(this, config)
        });
        return result;
    };
}

app.registerExtension({
    name: "comfy.dynamicLoraUI",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (NODE_CONFIGS[nodeData.name]) {
            setupDynamicNode(nodeType, nodeData);
        }
    },
    async setup() {
        console.log("✅ Dynamic LoRA UI extension loaded");
    }
});
