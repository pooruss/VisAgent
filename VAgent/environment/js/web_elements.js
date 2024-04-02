() => {
    return new Promise(resolve => {
        const elements = Array.from(document.querySelectorAll('*'));
        const validElements = [];
        const observers = [];
        let totalObserved = 0;

        for (const element of elements) {
            // 检查元素是否可见
            const isVisible = ((element.offsetWidth > 7 && element.offsetHeight > 7) && (element.getBoundingClientRect().width > 7 && element.getBoundingClientRect().height > 7));
            // 检查元素是否启用
            const isEnabled = !element.disabled;
            // 检查元素的计算样式
            const style = window.getComputedStyle(element);
            const isNotTransparent = style.opacity !== '0';
            const isNotHidden = style.visibility !== 'hidden' && style.display !== 'none';


            if (isVisible && isEnabled && (isCommonInteractiveElement(element) || (isNotTransparent && isNotHidden))) {
                const observer = new IntersectionObserver(entries => {
                    if (entries[0].isIntersecting) {
                        const bbox = element.getBoundingClientRect();
                        // 确保元素中央没有被其他元素遮挡
                        const topElement = document.elementFromPoint(bbox.x + bbox.width / 2, bbox.y + bbox.height / 2);
                        if (element.contains(topElement) || element === topElement) {
                            validElements.push(element);
                        }
                    }
                    observer.disconnect();
                    totalObserved++;

                    // 当所有元素都被观察后，解析Promise
                    if (totalObserved === elements.length) {
                        const interactiveElements = filterOutElements(validElements);
                        const elementsInfo = getElemInfos(interactiveElements);
                        // const elementsInfo = getElemInfos(validElements);
                        resolve(elementsInfo);
                    }
                });
                observers.push(observer);
                observer.observe(element);
            } else {
                totalObserved++;
            }
        }

        // 如果没有可见且启用的元素，立即解析Promise
        if (totalObserved === elements.length) {
            // resolve(validElements);
            const interactiveElements = filterOutElements(validElements);
            const elementsInfo = getElemInfos(interactiveElements);
            resolve(elementsInfo);
        }
    });

    function getElemInfos(elements) {
        const elemInfos = [];
        for (const element of elements) {
            const bbox = element.getBoundingClientRect();
            const selector = getSelector(element);
            const xpath = getElementXPath(element);
            const tagName = element.tagName;
            // return aria label if exists
            const ariaLabel = element.getAttribute('aria-label');
            const role = element.getAttribute('role');
            var text = '';

            if (ariaLabel) {
                text += ariaLabel;
            }
            if (role) {
                text += role;
            }

            if (text === '') {
                text = element.innerText;
            }

            elemInfos.push({ selector, xpath, bbox, tagName, text });
        }
        return elemInfos;
    }

    function getOverlapArea(a, b) {
        const x_overlap = Math.min(a.x, b.x);
        const y_overlap = Math.min(a.y, b.y);
        const x_max_overlap = Math.min(a.x + a.width, b.x + b.width);
        const y_max_overlap = Math.min(a.y + a.height, b.y + b.height);
        const width = x_max_overlap - x_overlap;
        const height = y_max_overlap - y_overlap;
        return width * height;
    }


    function isCommonInteractiveElement(element) {
        const tagName = element.tagName.toLowerCase();
        const interactiveTags = ['button', 'input', 'textarea', 'select', 'a'];

        if (interactiveTags.includes(tagName)) {
            return true;
        }

        // check role attribute
        const role = element.getAttribute("role");
        if (role) {
            const interactiveRoles = ['button', 'textbox', 'combobox', 'link', 'listbox', 'menu', 'menubar', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'option', 'radio', 'scrollbar', 'searchbox', 'slider', 'spinbutton', 'switch', 'tab', 'treeitem', 'application', 'document', 'checkbox'];
            return interactiveRoles.includes(role.toLowerCase());
        }

        return false;
    }

    function filterOutElements(elements) {
        var filteredElements = [];
        var filteredElements_area = [];
        // sort elements by area size, ascending
        elements.sort((a, b) => {
            const bboxa = a.getBoundingClientRect();
            const areaA = bboxa.width * bboxa.height;
            const bboxb = b.getBoundingClientRect();
            const areaB = bboxb.width * bboxb.height;
            return areaA - areaB;
        }
        );

        for (let i = 0; i < elements.length; i++) {
            const element = elements[i];
            bbox1 = element.getBoundingClientRect();
            let shouldRemove = false;
            for (let j = 0; j < filteredElements.length; j++) {
                const otherElement = filteredElements[j];
                const smallerArea = filteredElements_area[j];
                bbox2 = otherElement.getBoundingClientRect();
                const overlapArea = getOverlapArea(bbox1, bbox2);

                if (overlapArea / smallerArea > 0.8) {
                    if (!isCommonInteractiveElement(element)) {
                        shouldRemove = true;
                        break;
                    }else if (otherElement.contains(element)){
                        filteredElements[j] = element;
                        filteredElements_area[j] = bbox1.width * bbox1.height;
                        shouldRemove = true;
                        break;
                    }
                }
            }
            if (!shouldRemove) {
                filteredElements.push(element);
                filteredElements_area.push(bbox1.width * bbox1.height);
            }
        }

        return filteredElements;
    }



    function getElementXPath(element) {
        if (element.id !== '') {
            return `id("${element.id}")`;
        }
        if (element === document.body) {
            return '/html/body';
        }

        const siblings = Array.from(element.parentNode.childNodes).filter(sibling => sibling.nodeType === Node.ELEMENT_NODE);
        const index = siblings.indexOf(element) + 1; // XPath 是从 1 开始的
        return `${getElementXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${index}]`;
    }



    function getSelector(el) {
        if (el.id) {
            return '#' + el.id; // ID是唯一的，所以如果有ID就使用它
        }
        const tagName = el.tagName.toLowerCase();
        if (tagName === 'html') {
            return 'html';
        }
        // 如果元素是其父元素的唯一子元素，那么返回标签名
        if (el.parentNode && el.parentNode.children.length === 1) {
            return getSelector(el.parentNode) + ' > ' + tagName;
        }
        // 使用类名（如果有的话）和标签名
        const classNames = el.className.split(/\s+/).filter(Boolean).join('.');
        if (classNames) {
            return getSelector(el.parentNode) + ' > ' + tagName + '.' + classNames;
        }
        // 如果没有类名，尝试使用兄弟元素的数量来构建选择器
        let index = 1;
        for (let sibling = el.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
            index++;
        }
        return getSelector(el.parentNode) + ' > ' + tagName + ':nth-child(' + index + ')';
    }

}