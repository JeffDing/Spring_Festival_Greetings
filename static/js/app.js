// -*- coding: utf-8 -*-
/**
 * 春节祝福语生成器 - 前端交互逻辑
 */

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const yearInput = document.getElementById('year');
    const keywordInput = document.getElementById('keyword');
    const generateBtn = document.getElementById('generateBtn');
    const copyBtn = document.getElementById('copyBtn');
    const loading = document.getElementById('loading');
    const errorMsg = document.getElementById('errorMsg');
    const blessingText = document.getElementById('blessingText');
    const lunarYear = document.querySelector('.lunar-year');
    const zodiacText = document.querySelector('.zodiac');
    const copySuccess = document.getElementById('copySuccess');
    const fontSelect = document.getElementById('fontSelect');
    const saveBtn = document.getElementById('saveBtn');
    const paperBackground = document.querySelector('.paper-background');

    // 当前生成的祝福语
    let currentBlessing = '';

    // 年份输入验证 - 只在失去焦点或按回车时验证，不干扰输入过程
    yearInput.addEventListener('blur', function() {
        const year = parseInt(this.value);
        if (isNaN(year) || year < 1900) {
            this.value = 1900;
        } else if (year > 2100) {
            this.value = 2100;
        }
    });

    yearInput.addEventListener('change', function() {
        const year = parseInt(this.value);
        if (isNaN(year) || year < 1900) {
            this.value = 1900;
        } else if (year > 2100) {
            this.value = 2100;
        }
    });

    // 字体选择切换事件
    fontSelect.addEventListener('change', function() {
        const selectedFont = this.value;
        // 移除所有字体类
        blessingText.classList.remove('font-calligraphy', 'font-kaiti', 'font-songti', 'font-caoshu', 'font-yahei');
        // 添加选中的字体类
        blessingText.classList.add(`font-${selectedFont}`);
    });

    // 生成祝福语按钮点击事件
    generateBtn.addEventListener('click', async function() {
        // 隐藏错误消息
        errorMsg.classList.add('hidden');
        copySuccess.classList.add('hidden');

        // 获取表单数据
        const year = parseInt(yearInput.value);
        const categorySelect = document.getElementById('categorySelect');
        const styleSelect = document.getElementById('styleSelect');
        const category = categorySelect.value;
        const style = styleSelect.value;
        const keyword = keywordInput.value.trim();

        // 验证年份
        if (!year || year < 1900 || year > 2100) {
            showError('请输入1900-2100之间的有效年份');
            return;
        }

        // 显示加载动画
        loading.classList.remove('hidden');
        generateBtn.disabled = true;

        try {
            // 调用后端API
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    year: year,
                    category: category,
                    style: style,
                    keyword: keyword
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || '生成祝福语失败');
            }

            // 更新显示区域
            updateDisplay(data.blessing, data.lunar_year, data.zodiac);

            // 启用复制按钮
            copyBtn.disabled = false;
            // 启用保存按钮
            saveBtn.disabled = false;

        } catch (error) {
            showError(error.message || '生成祝福语时出错，请重试');
        } finally {
            // 隐藏加载动画
            loading.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    // 复制按钮点击事件
    copyBtn.addEventListener('click', async function() {
        if (!currentBlessing) {
            return;
        }

        try {
            // 尝试使用现代剪贴板API
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(currentBlessing);
            } else {
                // 降级方案：使用传统方法
                const textarea = document.createElement('textarea');
                textarea.value = currentBlessing;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
            }

            // 显示复制成功提示
            copySuccess.classList.remove('hidden');

            // 3秒后隐藏提示
            setTimeout(() => {
                copySuccess.classList.add('hidden');
            }, 3000);

        } catch (error) {
            showError('复制失败，请手动复制');
            console.error('复制错误:', error);
        }
    });

    // 保存为图片按钮点击事件
    saveBtn.addEventListener('click', async function() {
        if (!currentBlessing) {
            return;
        }

        try {
            // 显示加载提示
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 正在生成...';

            // 获取当前应用的字体类
            const currentFontClass = blessingText.className.split(' ').find(c => c.startsWith('font-'));
            
            // 使用html2canvas生成图片
            const canvas = await html2canvas(paperBackground, {
                backgroundColor: '#F5E6D3', // 宣纸色纯色背景
                scale: 2, // 提高清晰度
                useCORS: true, // 允许跨域图片
                logging: false,
                allowTaint: true,
                scrollX: 0,
                scrollY: 0,
                windowWidth: paperBackground.scrollWidth,
                windowHeight: paperBackground.scrollHeight,
                onclone: function(clonedDoc) {
                    // 在克隆的文档中确保字体样式正确应用
                    const clonedBlessingText = clonedDoc.getElementById('blessingText');
                    if (clonedBlessingText && currentFontClass) {
                        // 确保字体类被正确应用
                        clonedBlessingText.className = clonedBlessingText.className;
                    }
                    // 确保所有样式都被正确计算
                    const clonedPaper = clonedDoc.querySelector('.paper-background');
                    if (clonedPaper) {
                        clonedPaper.style.transform = 'none';
                        // 使用宣纸色纯色背景
                        clonedPaper.style.background = '#F5E6D3';
                        clonedPaper.style.backgroundImage = 'none';
                        clonedPaper.style.boxShadow = 'none';
                    }
                    // 移除伪元素边框，避免渲染问题
                    const style = clonedDoc.createElement('style');
                    style.textContent = `
                        .paper-background::before,
                        .paper-background::after {
                            display: none !important;
                        }
                    `;
                    clonedDoc.head.appendChild(style);
                }
            });

            // 创建下载链接
            const link = document.createElement('a');
            const timestamp = new Date().getTime();
            link.download = `春节祝福语_${timestamp}.png`;
            link.href = canvas.toDataURL('image/png');
            
            // 触发下载
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // 恢复按钮状态
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-download"></i> 保存为图片';

        } catch (error) {
            showError('保存图片失败，请重试');
            console.error('保存图片错误:', error);
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-download"></i> 保存为图片';
        }
    });

    // 更新显示区域
    function updateDisplay(blessing, lunarYearText, zodiacTextContent) {
        // 更新农历信息
        lunarYear.textContent = lunarYearText;
        zodiacText.textContent = `${zodiacTextContent}年大吉`;

        // 更新祝福语（将换行符转换为段落）
        const paragraphs = blessing.split('\n').filter(p => p.trim());
        blessingText.innerHTML = paragraphs.map(p => `<p>${p.trim()}</p>`).join('');

        // 保存当前祝福语
        currentBlessing = blessing;
    }

    // 显示错误消息
    function showError(message) {
        errorMsg.textContent = message;
        errorMsg.classList.remove('hidden');
    }

    // 页面加载时自动聚焦年份输入框
    yearInput.focus();

    // 支持回车键生成祝福语
    yearInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            generateBtn.click();
        }
    });

    // 添加动画效果到祝福语文本
    function animateBlessingText() {
        blessingText.style.opacity = '0';
        blessingText.style.transform = 'translateY(20px)';

        setTimeout(() => {
            blessingText.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            blessingText.style.opacity = '1';
            blessingText.style.transform = 'translateY(0)';
        }, 100);
    }

    // 监听祝福语变化，添加动画
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                animateBlessingText();
            }
        });
    });

    observer.observe(blessingText, {
        childList: true,
        subtree: true
    });

    // 添加键盘快捷键
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter 生成祝福语
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            generateBtn.click();
        }

        // Ctrl/Cmd + C 复制祝福语（当复制按钮可用时）
        if ((e.ctrlKey || e.metaKey) && e.key === 'c' && !copyBtn.disabled) {
            // 这里不阻止默认行为，让浏览器处理复制
        }
    });

    // 添加工具提示
    function addTooltip(element, text) {
        element.setAttribute('title', text);
    }

    addTooltip(generateBtn, '点击生成或按 Ctrl+Enter');
    addTooltip(copyBtn, '复制到剪贴板');

    // 初始化时设置默认年份为当前年份
    const currentYear = new Date().getFullYear();
    yearInput.value = currentYear;

    // 控制台欢迎信息
    console.log('%c春节祝福语生成器', 'font-size: 20px; font-weight: bold; color: #DC143C;');
    console.log('%cAI驱动 · 传统文化', 'font-size: 14px; color: #8B4513;');

    // ==================== 窗口自动缩放功能 ====================
    const container = document.querySelector('.container');
    const baseWidth = 1400; // 基准宽度
    const minScale = 0.5;   // 最小缩放比例
    const maxScale = 1.2;   // 最大缩放比例

    function updateScale() {
        const windowWidth = window.innerWidth;
        // 计算缩放比例，基于窗口宽度
        let scale = windowWidth / baseWidth;
        
        // 限制缩放范围
        scale = Math.max(minScale, Math.min(maxScale, scale));
        
        // 更新CSS变量
        document.documentElement.style.setProperty('--scale-factor', scale);
        
        // 更新基础字体大小
        const baseFontSize = 16 * scale;
        document.documentElement.style.setProperty('--base-font-size', `${baseFontSize}px`);
        
        // 对于大屏幕，使用transform缩放容器以获得更好的效果
        if (windowWidth >= baseWidth) {
            container.style.transform = `scale(${scale})`;
            container.style.transformOrigin = 'top center';
            // 补偿缩放带来的空间变化
            container.style.marginBottom = `${(1 - scale) * 100}%`;
        } else {
            // 小屏幕使用响应式布局，不使用transform
            container.style.transform = 'none';
            container.style.marginBottom = '0';
        }
    }

    // 初始化缩放
    updateScale();

    // 监听窗口大小变化
    let resizeTimeout;
    window.addEventListener('resize', function() {
        // 使用防抖优化性能
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(updateScale, 100);
    });

    // 监听设备方向变化（移动端）
    window.addEventListener('orientationchange', function() {
        setTimeout(updateScale, 200);
    });
});
