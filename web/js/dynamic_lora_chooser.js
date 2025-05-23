/**
 * Dynamic LoRA Chooser - Frontend Extension
 * Dynamically shows/hides slot widgets based on num_loras.
 */

import { app } from "../../scripts/app.js";

// Config for supported nodes
const NODE_CONFIGS = {
    "DynamicRandomLoraChooser": {
        maxSlots: 10,
        slotPrefix: "lora_",
        paramName: "num_loras",
        slotInputs: ["_name", "_min_strength", "_max_strength", "_weight", "_trigger_words"],
    },
    "SimpleRandomLoraChooser": {
        maxSlots: 8,
        slotPrefixes: ["lora_", "triggers_"],
        paramName: "num_loras",
    }
};

function hideWidget(widget) {
    if (!widget) return;
    if (widget._origType == null) widget._origType = widget.type;
    if (widget._origComputeSize == null) widget._origComputeSize = widget.computeSize;
    widget.type = "converted-widget";
    widget.computeSize = () => [0, -4];
    if (widget.linkedWidgets) {
        for (const w of widget.linkedWidgets) hideWidget(w);
    }
}

function showWidget(widget) {
    if (!widget) return;
    if (widget._origType) widget.type = widget._origType;
    if (widget._origComputeSize) widget.computeSize = widget._origComputeSize;
    delete widget._origType;
    delete widget._origComputeSize;
    if (widget.linkedWidgets) {
        for (const w of widget.linkedWidgets) showWidget(w);
    }
}

function updateDynamicLoraNodeVisibility(node, config) {
    if (!node.widgets) return;
    // Get num_loras
    const numWidget = node.widgets.find(w => w.name === config.paramName);
    let num_loras = 1;
    if (numWidget) num_loras = parseInt(numWidget.value) || 1;

    if (config.slotInputs) {
        // DynamicRandomLoraChooser style
        for (let i = 1; i <= config.maxSlots; i++) {
            const visible = i <= num_loras;
            for (const suffix of config.slotInputs) {
                const wName = `${config.slotPrefix}${i}${suffix}`;
                const w = node.widgets.find(w => w.name === wName);
                if (w) visible ? showWidget(w) : hideWidget(w);
            }
        }
    } else if (config.slotPrefixes) {
        // SimpleRandomLoraChooser style
        for (let i = 1; i <= config.maxSlots; i++) {
            const visible = i <= num_loras;
            for (const prefix of config.slotPrefixes) {
                const wName = `${prefix}${i}`;
                const w = node.widgets.find(w => w.name === wName);
                if (w) visible ? showWidget(w) : hideWidget(w);
            }
        }
    }

    // Redraw
    requestAnimationFrame(() => {
        node.setDirtyCanvas(true, true);
        if (node.onResize) node.onResize(node.size);
    });
}

function patchNodeType(nodeType, nodeName) {
    const config = NODE_CONFIGS[nodeName];
    if (!config) return;

    // Patch onNodeCreated (for new nodes)
    const origCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
        if (origCreated) origCreated.apply(this, arguments);
        setTimeout(() => updateDynamicLoraNodeVisibility(this, config), 50);
    };

    // Patch onConfigure (for loaded nodes)
    const origConfigure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function (info) {
        if (origConfigure) origConfigure.apply(this, arguments);
        setTimeout(() => updateDynamicLoraNodeVisibility(this, config), 50);
    };

    // Patch onWidgetChanged
    const origWidgetChanged = nodeType.prototype.onWidgetChanged;
    nodeType.prototype.onWidgetChanged = function (name, value, oldValue, widget) {
        if (origWidgetChanged) origWidgetChanged.apply(this, arguments);
        if (name === config.paramName) {
            updateDynamicLoraNodeVisibility(this, config);
        }
    };

    // Add a refresh option in menu
    const origMenu = nodeType.prototype.getExtraMenuOptions;
    nodeType.prototype.getExtraMenuOptions = function (_, options) {
        const res = origMenu ? origMenu.apply(this, arguments) : [];
        options.push({
            content: "🔄 Refresh Dynamic LoRA UI",
            callback: () => updateDynamicLoraNodeVisibility(this, config),
        });
        return res;
    };
}

app.registerExtension({
    name: "comfy.dynamicLoraChooser",
    beforeRegisterNodeDef(nodeType, nodeData, appRef) {
        if (NODE_CONFIGS[nodeData.name]) {
            patchNodeType(nodeType, nodeData.name);
        }
    },
    setup() {
        console.log("🎯 Dynamic LoRA Chooser frontend loaded!");
    }
});
