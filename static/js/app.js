document.addEventListener('DOMContentLoaded', () => {
    const groupsContainer = document.getElementById('groups-container');
    const addGroupButton = document.getElementById('add-group');
    const saveGroupsButton = document.getElementById('save-groups');
    let groups = [];
    let masonry;

    // Initialize Masonry
    function initMasonry() {
        const grid = document.getElementById('masonry-grid');
        masonry = new Masonry(grid, {
            itemSelector: '.masonry-item',
            columnWidth: '.masonry-item',
            percentPosition: true,
            gutter: 8
        });

        // Layout Masonry after images load
        const images = grid.getElementsByTagName('img');
        let loadedImages = 0;
        
        Array.from(images).forEach(img => {
            if (img.complete) {
                loadedImages++;
                if (loadedImages === images.length) {
                    masonry.layout();
                }
            } else {
                img.addEventListener('load', () => {
                    loadedImages++;
                    if (loadedImages === images.length) {
                        masonry.layout();
                    }
                });
            }
        });
    }

    // Create a new group
    function createGroup(groupData = null) {
        const groupId = groupData ? groupData.id : Date.now();
        const group = {
            id: groupId,
            element: document.createElement('div'),
            images: []
        };

        group.element.className = 'group';
        group.element.innerHTML = `
            <div class="group-header flex justify-between items-center mb-4">
                <div class="flex items-center space-x-2">
                    <input type="text" 
                           class="group-name text-lg font-semibold bg-transparent border-b border-gray-300 focus:border-blue-500 focus:outline-none px-1" 
                           placeholder="Group Name"
                           value="${groupData ? groupData.name || '' : ''}"
                    >
                </div>
                <button class="delete-group text-red-500 hover:text-red-700">Delete Group</button>
            </div>
            <div class="group-content min-h-[100px]"></div>
        `;

        group.element.querySelector('.delete-group').addEventListener('click', () => {
            group.element.remove();
            groups = groups.filter(g => g.id !== groupId);
        });

        groups.push(group);
        groupsContainer.appendChild(group.element);

        // If we have group data, add the images
        if (groupData && groupData.images) {
            groupData.images.forEach(imageUrl => {
                addImageToGroup(imageUrl, group);
            });
        }

        setupGroupDragAndDrop(group);
        return group;
    }

    // Load existing groups if any
    if (window.existingGroups && window.existingGroups.length > 0) {
        window.existingGroups.forEach(groupData => {
            createGroup(groupData);
        });
    } else {
        // Create initial group if no existing groups
        createGroup();
    }

    // Initialize Masonry
    initMasonry();

    // Add group button handler
    addGroupButton.addEventListener('click', () => createGroup());

    // Save groups handler
    saveGroupsButton.addEventListener('click', () => {
        const groupsData = groups.map(group => ({
            id: group.id,
            name: group.element.querySelector('.group-name').value || `Group ${groups.indexOf(group) + 1}`,
            images: group.images.map(img => img.getAttribute('data-image-url'))
        }));

        fetch('/save-groups', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(groupsData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success feedback
                saveGroupsButton.classList.add('bg-green-500');
                saveGroupsButton.classList.remove('bg-blue-500');
                setTimeout(() => {
                    saveGroupsButton.classList.remove('bg-green-500');
                    saveGroupsButton.classList.add('bg-blue-500');
                }, 2000);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Set up drag and drop for images in the gallery
    const galleryImages = document.querySelectorAll('#images-gallery .image-container');
    galleryImages.forEach(imageContainer => {
        imageContainer.addEventListener('dragstart', () => {
            imageContainer.classList.add('dragging');
        });

        imageContainer.addEventListener('dragend', () => {
            imageContainer.classList.remove('dragging');
        });
    });

    // Function to set up drag and drop for a group
    function setupGroupDragAndDrop(group) {
        group.element.addEventListener('dragover', (e) => {
            e.preventDefault();
            group.element.classList.add('drag-over');
        });

        group.element.addEventListener('dragleave', () => {
            group.element.classList.remove('drag-over');
        });

        group.element.addEventListener('drop', (e) => {
            e.preventDefault();
            group.element.classList.remove('drag-over');
            
            const draggingElement = document.querySelector('.dragging');
            if (draggingElement) {
                // If dragging from gallery, create a new image container
                if (draggingElement.closest('#images-gallery')) {
                    const imageUrl = draggingElement.getAttribute('data-image-url');
                    addImageToGroup(imageUrl, group);
                } 
                // If dragging between groups
                else {
                    const sourceGroup = groups.find(g => g.images.includes(draggingElement));
                    if (sourceGroup && sourceGroup !== group) {
                        sourceGroup.images = sourceGroup.images.filter(img => img !== draggingElement);
                        group.images.push(draggingElement);
                        group.element.querySelector('.group-content').appendChild(draggingElement);
                    }
                }
            }
        });
    }

    // Add image to group
    function addImageToGroup(imageUrl, group) {
        const imageContainer = document.createElement('div');
        imageContainer.className = 'image-container draggable';
        imageContainer.draggable = true;
        imageContainer.setAttribute('data-image-url', imageUrl);
        imageContainer.innerHTML = `
            <img src="${imageUrl}" alt="Grouped image">
            <div class="scene-id">${imageUrl.split('/').pop().split('.')[0]}</div>
            <div class="remove-btn">×</div>
        `;

        group.images.push(imageContainer);
        group.element.querySelector('.group-content').appendChild(imageContainer);

        // Remove image handler
        imageContainer.querySelector('.remove-btn').addEventListener('click', () => {
            imageContainer.remove();
            group.images = group.images.filter(img => img !== imageContainer);
        });

        // Drag and drop handlers for images
        imageContainer.addEventListener('dragstart', () => {
            imageContainer.classList.add('dragging');
        });

        imageContainer.addEventListener('dragend', () => {
            imageContainer.classList.remove('dragging');
        });
    }
}); 