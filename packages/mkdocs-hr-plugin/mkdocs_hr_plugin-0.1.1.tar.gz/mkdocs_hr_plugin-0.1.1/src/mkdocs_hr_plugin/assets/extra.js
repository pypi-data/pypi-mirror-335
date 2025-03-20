document.addEventListener('DOMContentLoaded', () => {
    let attempts = 0;
    const maxAttempts = 50;

    const waitForNav = setInterval(() => {
        attempts++;
        const nav = document.querySelector('.md-sidebar--secondary .md-nav__list');
        if (!nav) return;

        const navItems = Array.from(nav.querySelectorAll('.md-nav__item'));
        if (navItems.length === 0) {
            if (attempts >= maxAttempts) {
                clearInterval(waitForNav);
                console.error('目录加载超时');
            }
            return;
        }

        clearInterval(waitForNav);
        console.log('目录项数量:', navItems.length);

        // 获取主内容区域
        const mainContent = document.querySelector('.md-content__inner');
        if (!mainContent) return;

        // 获取所有标题
        const headings = Array.from(mainContent.querySelectorAll('h1, h2, h3, h4, h5, h6'));
        console.log('标题数量:', headings.length);

        // 收集所有分隔线位置
        const walker = document.createTreeWalker(mainContent, NodeFilter.SHOW_TEXT, {
            acceptNode: (node) => {
                if (!node || !node.textContent) return NodeFilter.FILTER_REJECT;
                if (node.parentElement?.closest('pre, code, .md-nav, script, style')) {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            }
        }, false);

        const hrPositions = [];
        let node;
        while (node = walker.nextNode()) {
            const text = node.textContent.trim();
            const match = text.match(/^---(.+?)---$/);
            if (match) {
                hrPositions.push({
                    node,
                    content: match[1].trim()
                });
            }
        }

        // 处理每个分隔线
        hrPositions.forEach((hrData, index) => {
            // 创建分隔线
            const hr = document.createElement('hr');
            hr.setAttribute('data-content', hrData.content);
            hr.classList.add('custom-hr');
            hr.id = `hr-${index + 1}`;
            hrData.node.parentNode.replaceChild(hr, hrData.node);

            // 创建目录项
            const li = document.createElement('li');
            li.classList.add('md-nav__item', 'hr-nav-item');
            const a = document.createElement('a');
            a.classList.add('md-nav__link');
            a.href = `#hr-${index + 1}`;
            a.textContent = `${hrData.content}`; // 修改这里，添加前后的破折号
            li.appendChild(a);



            // 找到分隔线后的第一个标题
            let nextHeadingIndex = -1;
            for (let i = 0; i < headings.length; i++) {
                const heading = headings[i];
                if (hr.compareDocumentPosition(heading) & Node.DOCUMENT_POSITION_FOLLOWING) {
                    nextHeadingIndex = i;
                    break;
                }
            }

            console.log('分隔线:', hrData.content, '下一个标题索引:', nextHeadingIndex);

            if (nextHeadingIndex !== -1) {
                // 找到对应的目录项
                const nextHeading = headings[nextHeadingIndex];
                const nextNavItem = navItems.find(item => {
                    const link = item.querySelector('a');
                    const text = link?.textContent?.replace('¶', '').trim();
                    return text === nextHeading.textContent.replace('¶', '').trim();
                });

                if (nextNavItem) {
                    nav.insertBefore(li, nextNavItem);
                    console.log('插入到标题前:', nextHeading.textContent);
                    return;
                }
            }

            nav.appendChild(li);
            console.log('追加到末尾:', hrData.content);
        });
    }, 100);
});