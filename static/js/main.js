/**
 * 交换机配置命令生成平台 - 主要JavaScript文件
 */

// 全局变量
let currentVendor = '';
let currentConfigType = '';

// DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * 初始化应用
 */
function initializeApp() {
    // 初始化工具提示
    initializeTooltips();
    
    // 初始化表单验证
    initializeFormValidation();
    
    // 绑定事件监听器
    bindEventListeners();
    
    console.log('应用初始化完成');
}

/**
 * 初始化Bootstrap工具提示
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * 初始化表单验证
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showToast('请填写所有必填字段', 'error');
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * 绑定事件监听器
 */
function bindEventListeners() {
    // 厂商选择变化事件
    const vendorSelect = document.getElementById('vendor');
    if (vendorSelect) {
        vendorSelect.addEventListener('change', handleVendorChange);
    }
    
    // 配置类型选择变化事件
    const configTypeSelect = document.getElementById('config_type');
    if (configTypeSelect) {
        configTypeSelect.addEventListener('change', handleConfigTypeChange);
    }
    
    // 表单重置事件
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', handleFormReset);
    }
}

/**
 * 处理厂商选择变化
 */
function handleVendorChange(event) {
    const vendor = event.target.value;
    currentVendor = vendor;
    
    const configTypeSelect = document.getElementById('config_type');
    const parametersSection = document.getElementById('parametersSection');
    const generateBtn = document.getElementById('generateBtn');
    
    if (vendor) {
        // 显示加载状态
        configTypeSelect.innerHTML = '<option value="">加载中...</option>';
        configTypeSelect.disabled = true;
        
        // 获取配置类型
        fetchConfigTypes(vendor)
            .then(configTypes => {
                populateConfigTypes(configTypes);
                configTypeSelect.disabled = false;
            })
            .catch(error => {
                console.error('获取配置类型失败:', error);
                showToast('获取配置类型失败，请重试', 'error');
                configTypeSelect.innerHTML = '<option value="">获取失败，请重试</option>';
            });
    } else {
        resetConfigTypeSelect();
        hideParametersSection();
        disableGenerateButton();
    }
}

/**
 * 处理配置类型选择变化
 */
function handleConfigTypeChange(event) {
    const configType = event.target.value;
    currentConfigType = configType;
    
    if (currentVendor && configType) {
        // 获取模板信息并生成参数表单
        fetchTemplateInfo(currentVendor, configType)
            .then(templateInfo => {
                generateParameterForm(templateInfo);
                showParametersSection();
                enableGenerateButton();
            })
            .catch(error => {
                console.error('获取模板信息失败:', error);
                showToast('获取模板信息失败，请重试', 'error');
                hideParametersSection();
                disableGenerateButton();
            });
    } else {
        hideParametersSection();
        disableGenerateButton();
    }
}

/**
 * 处理表单重置
 */
function handleFormReset() {
    currentVendor = '';
    currentConfigType = '';
    
    resetConfigTypeSelect();
    hideParametersSection();
    disableGenerateButton();
    
    // 清除验证状态
    const forms = document.querySelectorAll('.was-validated');
    forms.forEach(form => form.classList.remove('was-validated'));
    
    showToast('表单已重置', 'success');
}

/**
 * 获取配置类型
 */
async function fetchConfigTypes(vendor) {
    const response = await fetch(`/api/config_types/${vendor}`);
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error || '获取配置类型失败');
    }
    
    return data.config_types;
}

/**
 * 获取模板信息
 */
async function fetchTemplateInfo(vendor, configType) {
    const response = await fetch(`/api/template_info/${vendor}/${configType}`);
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error || '获取模板信息失败');
    }
    
    return data.template_info;
}

/**
 * 填充配置类型选择框
 */
function populateConfigTypes(configTypes) {
    const configTypeSelect = document.getElementById('config_type');
    configTypeSelect.innerHTML = '<option value="">请选择配置类型</option>';
    
    configTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.value;
        option.textContent = type.name;
        configTypeSelect.appendChild(option);
    });
}

/**
 * 重置配置类型选择框
 */
function resetConfigTypeSelect() {
    const configTypeSelect = document.getElementById('config_type');
    configTypeSelect.innerHTML = '<option value="">请先选择厂商</option>';
    configTypeSelect.disabled = true;
}

/**
 * 显示参数配置区域
 */
function showParametersSection() {
    const parametersSection = document.getElementById('parametersSection');
    if (parametersSection) {
        parametersSection.style.display = 'block';
        parametersSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * 隐藏参数配置区域
 */
function hideParametersSection() {
    const parametersSection = document.getElementById('parametersSection');
    if (parametersSection) {
        parametersSection.style.display = 'none';
    }
}

/**
 * 启用生成按钮
 */
function enableGenerateButton() {
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.disabled = false;
    }
}

/**
 * 禁用生成按钮
 */
function disableGenerateButton() {
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.disabled = true;
    }
}

/**
 * 生成参数表单
 */
function generateParameterForm(templateInfo) {
    const parametersContainer = document.getElementById('parametersContainer');
    if (!parametersContainer) return;
    
    parametersContainer.innerHTML = '';
    
    if (!templateInfo.parameters || Object.keys(templateInfo.parameters).length === 0) {
        parametersContainer.innerHTML = '<p class="text-muted">此配置类型无需额外参数</p>';
        return;
    }
    
    const parameters = templateInfo.parameters;
    
    // 创建参数表单
    for (const [paramName, paramConfig] of Object.entries(parameters)) {
        const formGroup = createParameterFormGroup(paramName, paramConfig);
        parametersContainer.appendChild(formGroup);
    }
    
    // 添加示例数据按钮
    if (templateInfo.example) {
        const exampleBtn = createExampleButton(templateInfo.example);
        parametersContainer.appendChild(exampleBtn);
    }
}

/**
 * 创建参数表单组
 */
function createParameterFormGroup(paramName, paramConfig) {
    const formGroup = document.createElement('div');
    formGroup.className = 'mb-3';
    
    const isRequired = paramConfig.required || false;
    const requiredAttr = isRequired ? 'required' : '';
    const requiredLabel = isRequired ? '<span class="text-danger">*</span>' : '';
    
    let inputHtml = '';
    
    if (paramConfig.options) {
        // 下拉选择
        inputHtml = createSelectInput(paramName, paramConfig, requiredAttr, requiredLabel);
    } else if (paramConfig.type === 'list') {
        // 列表输入
        inputHtml = createListInput(paramName, paramConfig, requiredAttr, requiredLabel);
    } else if (paramConfig.type === 'integer') {
        // 数字输入
        inputHtml = createNumberInput(paramName, paramConfig, requiredAttr, requiredLabel);
    } else {
        // 文本输入
        inputHtml = createTextInput(paramName, paramConfig, requiredAttr, requiredLabel);
    }
    
    formGroup.innerHTML = inputHtml;
    return formGroup;
}

/**
 * 创建下拉选择输入
 */
function createSelectInput(paramName, paramConfig, requiredAttr, requiredLabel) {
    const options = paramConfig.options.map(option => 
        `<option value="${option}">${option}</option>`
    ).join('');
    
    return `
        <label for="${paramName}" class="form-label">
            ${paramConfig.description || paramName} ${requiredLabel}
        </label>
        <select class="form-select" id="${paramName}" name="${paramName}" ${requiredAttr}>
            <option value="">请选择</option>
            ${options}
        </select>
    `;
}

/**
 * 创建列表输入
 */
function createListInput(paramName, paramConfig, requiredAttr, requiredLabel) {
    return `
        <label for="${paramName}" class="form-label">
            ${paramConfig.description || paramName} ${requiredLabel}
        </label>
        <input type="text" class="form-control" id="${paramName}" name="${paramName}" ${requiredAttr}
               placeholder="多个值请用逗号分隔，如：值1,值2,值3">
        <div class="form-help">多个值请用逗号分隔</div>
    `;
}

/**
 * 创建数字输入
 */
function createNumberInput(paramName, paramConfig, requiredAttr, requiredLabel) {
    const min = paramConfig.range ? paramConfig.range[0] : '';
    const max = paramConfig.range ? paramConfig.range[1] : '';
    const rangeHelp = paramConfig.range ? 
        `<div class="form-help">范围: ${paramConfig.range[0]} - ${paramConfig.range[1]}</div>` : '';
    
    return `
        <label for="${paramName}" class="form-label">
            ${paramConfig.description || paramName} ${requiredLabel}
        </label>
        <input type="number" class="form-control" id="${paramName}" name="${paramName}" ${requiredAttr}
               ${min ? `min="${min}"` : ''} ${max ? `max="${max}"` : ''}>
        ${rangeHelp}
    `;
}

/**
 * 创建文本输入
 */
function createTextInput(paramName, paramConfig, requiredAttr, requiredLabel) {
    const maxLength = paramConfig.max_length ? `maxlength="${paramConfig.max_length}"` : '';
    const lengthHelp = paramConfig.max_length ? 
        `<div class="form-help">最大长度: ${paramConfig.max_length} 个字符</div>` : '';
    
    return `
        <label for="${paramName}" class="form-label">
            ${paramConfig.description || paramName} ${requiredLabel}
        </label>
        <input type="text" class="form-control" id="${paramName}" name="${paramName}" ${requiredAttr} ${maxLength}>
        ${lengthHelp}
    `;
}

/**
 * 创建示例数据按钮
 */
function createExampleButton(example) {
    const exampleBtn = document.createElement('button');
    exampleBtn.type = 'button';
    exampleBtn.className = 'btn btn-outline-info btn-sm mt-2';
    exampleBtn.innerHTML = '<i class="fas fa-lightbulb me-1"></i>填入示例数据';
    exampleBtn.addEventListener('click', function() {
        fillExampleData(example);
    });
    return exampleBtn;
}

/**
 * 填入示例数据
 */
function fillExampleData(example) {
    for (const [key, value] of Object.entries(example)) {
        const input = document.getElementById(key);
        if (input) {
            if (Array.isArray(value)) {
                input.value = value.join(', ');
            } else {
                input.value = value;
            }
        }
    }
    showToast('示例数据已填入', 'success');
}
