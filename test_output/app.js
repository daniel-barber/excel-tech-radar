// ===== Radar Visualization with D3.js =====

// Global state
let radarData = null;
let currentFilter = '';
let selectedEntry = null;

// ===== Data Loading =====
async function loadRadarData() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    
    loading.classList.remove('hidden');
    
    try {
        // Try to load from embedded JSON first (for file:// protocol)
        const embeddedData = document.getElementById('radar-data');
        if (embeddedData) {
            radarData = JSON.parse(embeddedData.textContent);
            console.log('Loaded embedded radar data');
        } else {
            // Fetch from radar.json
            const response = await fetch('radar.json');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            radarData = await response.json();
            console.log('Loaded radar.json');
        }
        
        loading.classList.add('hidden');
        initializeRadar();
    } catch (err) {
        console.error('Failed to load radar data:', err);
        loading.classList.add('hidden');
        error.classList.remove('hidden');
        document.getElementById('error-message').textContent = err.message;
    }
}

// ===== Radar Initialization =====
function initializeRadar() {
    // Update header with data from radar.json
    if (radarData.meta.title) {
        document.getElementById('radar-title').textContent = radarData.meta.title;
    }
    if (radarData.meta.subtitle) {
        document.getElementById('radar-subtitle').textContent = radarData.meta.subtitle;
    }
    
    // Build legend
    buildLegend();
    
    // Render radar
    renderRadar();
    
    // Setup interactions
    setupSearch();
    setupKeyboardNavigation();
}

// ===== Legend =====
function buildLegend() {
    const ringsContainer = document.getElementById('legend-rings');
    const statusesContainer = document.getElementById('legend-statuses');
    const dealSizesContainer = document.getElementById('legend-dealsizes');
    
    // Rings
    ringsContainer.innerHTML = '<h4 style="font-size: 0.9rem; margin-bottom: 0.5rem;">Rings</h4>';
    radarData.rings.forEach(ring => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `
            <div class="legend-color" style="background: ${ring.color};"></div>
            <span>${ring.name}</span>
        `;
        ringsContainer.appendChild(item);
    });
    
    // Statuses
    if (radarData.statuses && radarData.statuses.length > 0) {
        statusesContainer.innerHTML = '<h4 style="font-size: 0.9rem; margin-bottom: 0.5rem; margin-top: 1rem;">Status</h4>';
        radarData.statuses.forEach(status => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = `
                <div class="legend-color" style="background: ${status.color};"></div>
                <span>${status.name}</span>
            `;
            statusesContainer.appendChild(item);
        });
    }
    
    // Deal Sizes
    if (radarData.dealSizes && radarData.dealSizes.length > 0) {
        dealSizesContainer.innerHTML = '<h4 style="font-size: 0.9rem; margin-bottom: 0.5rem; margin-top: 1rem;">Deal Size</h4>';
        radarData.dealSizes.forEach(dealSize => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            // Calculate circle size based on value (1, 2, 3) mapped to dotMinSize to dotMaxSize
            const minSize = radarData.layout.dotMinSize;
            const maxSize = radarData.layout.dotMaxSize;
            const maxValue = Math.max(...radarData.dealSizes.map(d => d.value));
            const circleSize = minSize + (maxSize - minSize) * ((dealSize.value - 1) / (maxValue - 1));
            
            item.innerHTML = `
                <div class="legend-size" style="width: ${circleSize}px; height: ${circleSize}px; border-radius: 50%; background: #666; display: inline-block; vertical-align: middle;"></div>
                <span style="margin-left: 8px;">${dealSize.name}</span>
            `;
            dealSizesContainer.appendChild(item);
        });
    }
}

// ===== Radar Rendering =====
function renderRadar() {
    const svg = d3.select('#radar-svg');
    const container = document.getElementById('radar-container');
    const width = Math.min(container.clientWidth - 40, 1200);
    const height = Math.min(container.clientHeight - 40, 1200);
    
    svg.attr('width', width).attr('height', height);
    
    const centerX = width / 2;
    const centerY = height / 2;
    
    const layout = radarData.layout;
    const minRadius = layout.minRadius;
    const maxRadius = Math.min(width, height) / 2 - 80;
    
    // Calculate ring radii
    const ringCount = radarData.rings.length;
    const ringRadii = radarData.rings.map((ring, i) => {
        return minRadius + (maxRadius - minRadius) * (i + 1) / ringCount;
    });
    
    // Clear existing content
    const g = svg.select('#radar-group');
    g.selectAll('*').remove();
    
    // Add zoom behavior with proper centering
    const zoom = d3.zoom()
        .scaleExtent([0.5, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform.toString() + ` translate(${centerX}, ${centerY})`);
        });
    
    svg.call(zoom);
    
    // Reset zoom on double-click
    svg.on('dblclick.zoom', () => {
        svg.transition()
            .duration(750)
            .call(zoom.transform, d3.zoomIdentity);
    });
    
    // Zoom control buttons - zoom to center
    document.getElementById('zoom-in').onclick = () => {
        svg.transition()
            .duration(300)
            .call(zoom.scaleBy, 1.3);
    };
    
    document.getElementById('zoom-out').onclick = () => {
        svg.transition()
            .duration(300)
            .call(zoom.scaleBy, 0.7);
    };
    
    document.getElementById('zoom-reset').onclick = () => {
        svg.transition()
            .duration(750)
            .call(zoom.transform, d3.zoomIdentity);
    };
    
    // Export to PNG button
    document.getElementById('export-png').onclick = () => {
        exportRadarToPNG(svg, radarData.meta.title);
    };
    
    // Initial transform
    g.attr('transform', `translate(${centerX}, ${centerY})`);
    
    // Draw rings
    radarData.rings.forEach((ring, i) => {
        const radius = ringRadii[i];
        
        // Ring circle
        g.append('circle')
            .attr('class', 'ring-circle')
            .attr('r', radius)
            .attr('stroke', ring.color)
            .attr('stroke-width', 2);
        
        // Ring label
        g.append('text')
            .attr('class', 'ring-label')
            .attr('y', -radius + 20)
            .attr('text-anchor', 'middle')
            .text(ring.name)
            .style('fill', ring.color);
    });
    
    // Draw quadrant lines
    const quadrantCount = radarData.quadrants.length;
    const angleStep = (2 * Math.PI) / quadrantCount;
    const startAngle = (layout.startAngleDeg * Math.PI) / 180;
    
    radarData.quadrants.forEach((quadrant, i) => {
        const angle = startAngle + i * angleStep;
        const x = Math.cos(angle) * maxRadius;
        const y = Math.sin(angle) * maxRadius;
        
        // Quadrant line
        g.append('line')
            .attr('class', 'quadrant-line')
            .attr('x1', 0)
            .attr('y1', 0)
            .attr('x2', x)
            .attr('y2', y);
        
        // Quadrant label
        const labelAngle = angle + angleStep / 2;
        const labelRadius = maxRadius + 30;
        const labelX = Math.cos(labelAngle) * labelRadius;
        const labelY = Math.sin(labelAngle) * labelRadius;
        
        g.append('text')
            .attr('class', 'quadrant-label')
            .attr('x', labelX)
            .attr('y', labelY)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .text(quadrant.name);
    });
    
    // Position entries
    const positionedEntries = positionEntries(radarData.entries, {
        rings: radarData.rings,
        quadrants: radarData.quadrants,
        ringRadii,
        angleStep,
        startAngle,
        jitter: layout.jitter,
        minRadius,
    });
    
    // Draw entries (dots)
    const dots = g.selectAll('.radar-dot')
        .data(positionedEntries)
        .enter()
        .append('circle')
        .attr('class', d => {
            let classes = 'radar-dot';
            if (d.status) classes += ` status-${d.status}`;
            if (d.isNew) classes += ' is-new';
            return classes;
        })
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .attr('r', d => calculateDotSize(d, layout))
        .attr('fill', d => {
            const ring = radarData.rings.find(r => r.id === d.ring);
            return ring ? ring.color : '#999';
        })
        .attr('stroke', d => {
            if (d.status) {
                const status = radarData.statuses.find(s => s.id === d.status);
                return status ? status.color : '#333';
            }
            return '#333';
        })
        .attr('stroke-width', d => d.isNew ? 3 : 1.5)
        .attr('opacity', 0.85)
        .on('mouseenter', handleDotHover)
        .on('mouseleave', handleDotLeave)
        .on('click', handleDotClick);
    
    // Draw labels below dots
    const labels = g.selectAll('.radar-label')
        .data(positionedEntries)
        .enter()
        .append('text')
        .attr('class', 'radar-label')
        .attr('x', d => d.x)
        .attr('y', d => d.y + calculateDotSize(d, layout) + 12)
        .attr('text-anchor', 'middle')
        .attr('font-size', '10px')
        .attr('font-weight', '500')
        .attr('fill', '#333')
        .attr('pointer-events', 'none')
        .text(d => d.name)
        .on('mouseenter', handleDotHover)
        .on('click', handleDotClick);
    
    // Apply force simulation for collision avoidance
    applyForceLayout(dots, labels, positionedEntries, {
        ringRadii,
        angleStep,
        startAngle,
        quadrantCount,
    });
}

// ===== Entry Positioning =====
function positionEntries(entries, config) {
    const { rings, quadrants, ringRadii, angleStep, startAngle, jitter, minRadius } = config;
    
    return entries.map(entry => {
        // Find ring index
        const ringIndex = rings.findIndex(r => r.id === entry.ring);
        const ringRadius = ringIndex === 0 
            ? minRadius + (ringRadii[0] - minRadius) / 2
            : (ringRadii[ringIndex - 1] + ringRadii[ringIndex]) / 2;
        
        // Find quadrant index
        const quadrantIndex = quadrants.findIndex(q => q.id === entry.quadrant);
        
        // Calculate base angle (middle of quadrant)
        const baseAngle = startAngle + quadrantIndex * angleStep + angleStep / 2;
        
        // Add jitter
        const angleJitter = (Math.random() - 0.5) * angleStep * jitter * 0.8;
        const radiusJitter = (Math.random() - 0.5) * (ringRadii[ringIndex] - (ringIndex > 0 ? ringRadii[ringIndex - 1] : minRadius)) * jitter;
        
        const angle = baseAngle + angleJitter;
        const radius = ringRadius + radiusJitter;
        
        return {
            ...entry,
            x: Math.cos(angle) * radius,
            y: Math.sin(angle) * radius,
            angle,
            radius,
            ringIndex,
            quadrantIndex,
        };
    });
}

// ===== Force Layout =====
function applyForceLayout(dots, labels, entries, config) {
    const { ringRadii, angleStep, startAngle, quadrantCount } = config;
    
    const simulation = d3.forceSimulation(entries)
        .force('collision', d3.forceCollide().radius(d => calculateDotSize(d, radarData.layout) + 15))
        .force('constrain', () => {
            entries.forEach(d => {
                // Constrain to quadrant
                const minAngle = startAngle + d.quadrantIndex * angleStep;
                const maxAngle = minAngle + angleStep;
                
                let angle = Math.atan2(d.y, d.x);
                if (angle < 0) angle += 2 * Math.PI;
                
                if (angle < minAngle) angle = minAngle + 0.01;
                if (angle > maxAngle) angle = maxAngle - 0.01;
                
                // Constrain to ring
                const minRingRadius = d.ringIndex > 0 ? ringRadii[d.ringIndex - 1] : 0;
                const maxRingRadius = ringRadii[d.ringIndex];
                
                let radius = Math.sqrt(d.x * d.x + d.y * d.y);
                if (radius < minRingRadius) radius = minRingRadius + 5;
                if (radius > maxRingRadius) radius = maxRingRadius - 5;
                
                d.x = Math.cos(angle) * radius;
                d.y = Math.sin(angle) * radius;
            });
        })
        .alpha(0.3)
        .alphaDecay(0.05)
        .on('tick', () => {
            dots.attr('cx', d => d.x).attr('cy', d => d.y);
            labels.attr('x', d => d.x)
                  .attr('y', d => d.y + calculateDotSize(d, radarData.layout) + 12);
        });
}

// ===== Dot Size Calculation =====
function calculateDotSize(entry, layout) {
    if (entry.value && entry.value > 0) {
        // Size based on value
        const maxValue = Math.max(...radarData.entries.map(e => e.value || 0));
        const normalized = entry.value / maxValue;
        return layout.dotMinSize + (layout.dotMaxSize - layout.dotMinSize) * normalized;
    }
    return (layout.dotMinSize + layout.dotMaxSize) / 2;
}

// ===== Interactions =====
function handleDotHover(event, d) {
    const tooltip = document.getElementById('tooltip');
    
    // Highlight dot
    d3.select(event.target).classed('highlighted', true);
    
    // Show tooltip
    const ring = radarData.rings.find(r => r.id === d.ring);
    const quadrant = radarData.quadrants.find(q => q.id === d.quadrant);
    const status = d.status ? radarData.statuses.find(s => s.id === d.status) : null;
    
    let content = `<strong>${d.name}</strong><br>`;
    content += `${ring.name} • ${quadrant.name}`;
    if (status) content += `<br>Status: ${status.name}`;
    if (d.isNew) content += '<br><em>New</em>';
    
    tooltip.innerHTML = content;
    tooltip.classList.remove('hidden');
    
    // Position tooltip
    tooltip.style.left = `${event.pageX + 10}px`;
    tooltip.style.top = `${event.pageY + 10}px`;
}

function handleDotLeave(event) {
    d3.select(event.target).classed('highlighted', false);
    document.getElementById('tooltip').classList.add('hidden');
}

function handleDotClick(event, d) {
    selectedEntry = d;
    showDetailPanel(d);
}

// ===== Detail Panel =====
function showDetailPanel(entry) {
    const panel = document.getElementById('detail-panel');
    
    // Populate content
    document.getElementById('detail-name').textContent = entry.name;
    
    // Meta badges
    const ring = radarData.rings.find(r => r.id === entry.ring);
    const quadrant = radarData.quadrants.find(q => q.id === entry.quadrant);
    const status = entry.status ? radarData.statuses.find(s => s.id === entry.status) : null;
    
    document.getElementById('detail-ring').textContent = ring.name;
    document.getElementById('detail-ring').style.background = ring.color;
    document.getElementById('detail-ring').style.color = '#fff';
    
    document.getElementById('detail-quadrant').textContent = quadrant.name;
    
    if (status) {
        document.getElementById('detail-status').textContent = status.name;
        document.getElementById('detail-status').style.background = status.color;
        document.getElementById('detail-status').style.color = '#fff';
        document.getElementById('detail-status').style.display = 'inline-block';
    } else {
        document.getElementById('detail-status').style.display = 'none';
    }
    
    // Tags
    const tagsContainer = document.getElementById('detail-tags');
    tagsContainer.innerHTML = '';
    if (entry.tags && entry.tags.length > 0) {
        entry.tags.forEach(tag => {
            const tagEl = document.createElement('span');
            tagEl.className = 'tag';
            tagEl.textContent = tag;
            tagsContainer.appendChild(tagEl);
        });
    }
    
    // Description
    document.getElementById('detail-description').innerHTML = entry.descriptionHtml || '<p><em>No description available</em></p>';
    
    // Extra info
    const extraContainer = document.getElementById('detail-extra');
    extraContainer.innerHTML = '';
    if (entry.customer || entry.value || entry.owner) {
        let extraHtml = '';
        if (entry.customer) extraHtml += `<p><strong>Customer:</strong> ${entry.customer}</p>`;
        if (entry.value) extraHtml += `<p><strong>Value:</strong> $${entry.value.toLocaleString()}</p>`;
        if (entry.owner) extraHtml += `<p><strong>Owner:</strong> ${entry.owner}</p>`;
        extraContainer.innerHTML = extraHtml;
    }
    
    // Link
    const linkContainer = document.getElementById('detail-link');
    linkContainer.innerHTML = '';
    if (entry.link) {
        linkContainer.innerHTML = `<a href="${entry.link}" target="_blank" rel="noopener noreferrer">View Details →</a>`;
    }
    
    // Show panel
    panel.classList.remove('hidden');
}

function closeDetailPanel() {
    document.getElementById('detail-panel').classList.add('hidden');
    selectedEntry = null;
}

// ===== Search & Filter =====
function setupSearch() {
    const searchBox = document.getElementById('search-box');
    const clearButton = document.getElementById('clear-search');
    
    searchBox.addEventListener('input', (e) => {
        currentFilter = e.target.value.toLowerCase();
        applyFilters();
    });
    
    clearButton.addEventListener('click', () => {
        searchBox.value = '';
        currentFilter = '';
        applyFilters();
    });
}

function setupFilters() {
    // Filters removed for cleaner UI
}

function applyFilters() {
    const filterFunc = function(d) {
        // Search filter only
        if (currentFilter) {
            const matchesName = d.name.toLowerCase().includes(currentFilter);
            const matchesTags = d.tags && d.tags.some(tag => tag.toLowerCase().includes(currentFilter));
            if (!matchesName && !matchesTags) return true;
        }
        
        return false;
    };
    
    // Apply filter to both dots and labels
    d3.selectAll('.radar-dot').classed('filtered', filterFunc);
    d3.selectAll('.radar-label').classed('filtered', filterFunc);
}

// ===== Keyboard Navigation =====
function setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeDetailPanel();
        }
    });
    
    document.getElementById('close-panel').addEventListener('click', closeDetailPanel);
}

// ===== Export to PNG =====
function exportRadarToPNG(svg, title) {
    // Get the SVG element and clone it
    const svgElement = svg.node();
    
    // Get the radar group and save its current transform
    const radarGroup = svgElement.querySelector('#radar-group');
    const originalTransform = radarGroup.getAttribute('transform');
    
    // Temporarily reset transform to capture full radar
    const svgWidth = svgElement.width.baseVal.value;
    const svgHeight = svgElement.height.baseVal.value;
    const svgCenterX = svgWidth / 2;
    const svgCenterY = svgHeight / 2;
    radarGroup.setAttribute('transform', `translate(${svgCenterX}, ${svgCenterY})`);
    
    // Clone after resetting transform
    const clone = svgElement.cloneNode(true);
    
    // Restore original transform
    radarGroup.setAttribute('transform', originalTransform);
    
    // Get computed styles and apply them inline
    const allElements = clone.querySelectorAll('*');
    const originalElements = svgElement.querySelectorAll('*');
    
    allElements.forEach((el, i) => {
        const original = originalElements[i];
        if (original) {
            const computedStyle = window.getComputedStyle(original);
            let styleStr = '';
            
            // Copy important style properties
            const importantProps = [
                'fill', 'stroke', 'stroke-width', 'font-family', 'font-size',
                'font-weight', 'text-anchor', 'opacity', 'stroke-dasharray', 'stroke-opacity'
            ];
            
            importantProps.forEach(prop => {
                const value = computedStyle.getPropertyValue(prop);
                if (value) {
                    // Include 'none' for fill property (important for ring circles)
                    if (prop === 'fill' || value !== 'none' && value !== 'normal') {
                        styleStr += `${prop}:${value};`;
                    }
                }
            });
            
            // Special handling for ring circles - ensure they have no fill
            if (el.classList && el.classList.contains('ring-circle')) {
                styleStr += 'fill:none;';
            }
            
            if (styleStr) {
                el.setAttribute('style', styleStr);
            }
        }
    });
    
    // Serialize the styled SVG
    const svgData = new XMLSerializer().serializeToString(clone);
    
    // Create canvas
    const canvas = document.createElement('canvas');
    const width = svgElement.width.baseVal.value;
    const height = svgElement.height.baseVal.value;
    
    canvas.width = width * 2; // 2x for quality
    canvas.height = height * 2;
    
    const ctx = canvas.getContext('2d');
    ctx.scale(2, 2);
    
    // White background
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(0, 0, width, height);
    
    // Create image from SVG
    const img = new Image();
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);
    
    img.onload = function() {
        ctx.drawImage(img, 0, 0);
        URL.revokeObjectURL(url);
        
        // Download
        canvas.toBlob(function(blob) {
            const link = document.createElement('a');
            const filename = `${title.replace(/\s+/g, '-').toLowerCase()}-radar.png`;
            link.download = filename;
            link.href = URL.createObjectURL(blob);
            link.click();
            URL.revokeObjectURL(link.href);
        });
    };
    
    img.onerror = function(e) {
        console.error('Error loading SVG:', e);
        alert('Export failed. Please try again.');
    };
    
    img.src = url;
}

// ===== Initialize on Load =====
document.addEventListener('DOMContentLoaded', loadRadarData);

// Handle window resize
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        if (radarData) renderRadar();
    }, 250);
});

// Made with Bob
