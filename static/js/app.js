document.addEventListener('DOMContentLoaded', () => {
    const groupsContainer = document.getElementById('groups-container');
    const addGroupButton = document.getElementById('add-group');
    let groups = [];

    // Create a new group
    function createGroup() {
        const groupId = Date.now();
        const group = {
            id: groupId,
            element: document.createElement('div'),
            images: []
        };

        group.element.className = 'group';
        group.element.innerHTML = `
            <div class="group-header flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold">Group ${groups.length + 1}</h3>
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
        return group;
    }

    // Create initial group
    createGroup();

    // Add group button handler
    addGroupButton.addEventListener('click', createGroup);

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

    // Set up drag and drop for groups
    groups.forEach(group => {
        setupGroupDragAndDrop(group);
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