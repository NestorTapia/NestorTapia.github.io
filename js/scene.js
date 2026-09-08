import * as THREE from './vendor/three.module.min.js';

const host = document.querySelector('#architecture-scene');
const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');

if (host) {
    try {
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
        renderer.setPixelRatio(Math.min(devicePixelRatio, 1.35));
        renderer.setClearColor(0x0b0e11, 0);
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        host.append(renderer.domElement);

        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(-10, 10, 5, -5, .1, 100);
        camera.position.set(10, 11, 14);
        camera.lookAt(0, 0, 0);
        const ambient = new THREE.AmbientLight(0xcedde5, 2);
        scene.add(ambient);
        const key = new THREE.DirectionalLight(0xffffff, 3.5);
        key.position.set(1, 8, 5);
        scene.add(key);
        const rim = new THREE.DirectionalLight(0x72dee0, 2.5);
        rim.position.set(-5, 2, -4);
        scene.add(rim);
        const warm = new THREE.PointLight(0xff704f, 15, 12);
        warm.position.set(1, 3, 1);
        scene.add(warm);

        const coreAssembly = new THREE.Group();
        scene.add(coreAssembly);
        const metal = new THREE.MeshStandardMaterial({ color: 0x273139, metalness: .7, roughness: .35 });
        const pale = new THREE.MeshStandardMaterial({ color: 0x8eaaa9, metalness: .55, roughness: .35 });
        const orange = new THREE.MeshBasicMaterial({ color: 0xff7557 });
        const mint = new THREE.MeshBasicMaterial({ color: 0x80e3dc });

        function edgedBox(width, height, depth, material, position, lineColor = 0x597078, group = coreAssembly) {
            const geometry = new THREE.BoxGeometry(width, height, depth);
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(...position);
            const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geometry), new THREE.LineBasicMaterial({ color: lineColor, transparent: true, opacity: .65 }));
            mesh.add(edges);
            group.add(mesh);
            return mesh;
        }

        function label(text, x, y, z, width, color = '#e6eff0', group = coreAssembly) {
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 160;
            const ctx = canvas.getContext('2d');
            ctx.font = '600 55px monospace';
            ctx.fillStyle = color;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(text, 256, 80);
            const texture = new THREE.CanvasTexture(canvas);
            texture.colorSpace = THREE.SRGBColorSpace;
            const plane = new THREE.Mesh(new THREE.PlaneGeometry(width, width / 3.2), new THREE.MeshBasicMaterial({ map: texture, transparent: true, depthWrite: false }));
            plane.rotation.x = -Math.PI / 2;
            plane.position.set(x, y, z);
            group.add(plane);
        }

        const core = new THREE.Mesh(
            new THREE.IcosahedronGeometry(1.35, 1),
            new THREE.MeshStandardMaterial({ color: 0x6e9697, metalness: .72, roughness: .22, flatShading: true })
        );
        core.position.y = .72;
        coreAssembly.add(core);
        const coreWire = new THREE.LineSegments(
            new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(1.38, 1)),
            new THREE.LineBasicMaterial({ color: 0xb6eeea, transparent: true, opacity: .6 })
        );
        coreWire.position.copy(core.position);
        coreAssembly.add(coreWire);
        const coreRings = [];
        [[2.2, 0xff7557, .16], [2.75, 0x80e3dc, -.22], [3.35, 0x7898a1, .44]].forEach(([radius, color, tilt], index) => {
            const ring = new THREE.Mesh(new THREE.TorusGeometry(radius, index === 0 ? .035 : .018, 8, 96), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: index === 2 ? .45 : .85 }));
            ring.rotation.x = Math.PI / 2 + tilt;
            ring.rotation.z = index * .45;
            ring.position.y = .72;
            coreAssembly.add(ring);
            coreRings.push(ring);
        });
        const corePackets = [];
        const nodePositions = [[-3.5, .1, -1.6], [-3.4, .1, 1.8], [3.4, .1, -1.7], [3.65, .1, 1.45], [0, .1, 3.5]];
        nodePositions.forEach((position, index) => {
            edgedBox(1.05, .2, .78, index % 2 ? pale : metal, position, index % 2 ? 0x80e3dc : 0xff7557, coreAssembly);
            edgedBox(.68, .035, .035, index % 2 ? mint : orange, [position[0], .23, position[2] + .4], index % 2 ? 0x80e3dc : 0xff7557, coreAssembly);
            const curve = new THREE.CatmullRomCurve3([
                new THREE.Vector3(position[0], .2, position[2]),
                new THREE.Vector3(position[0] * .58, .35, position[2] * .58),
                new THREE.Vector3(0, .72, 0),
            ], false, 'centripetal');
            coreAssembly.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 42, .014, 5, false), index % 2 ? mint : orange));
            const packet = new THREE.Mesh(new THREE.SphereGeometry(.07, 10, 10), index % 2 ? mint : orange);
            coreAssembly.add(packet);
            corePackets.push({ mesh: packet, curve, offset: index * .19 });
        });
        label('NÚCLEO PYTHON', 0, 2.28, 0, 2.1, '#eaf8f6', coreAssembly);

        let paused = motionPreference.matches;
        let visible = true;
        let scrolling = false;
        let scrollTimer = 0;
        let frame = 0;
        let last = 0;
        let elapsed = 0;
        let pointerX = 0;
        let pointerY = 0;
        const right = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 0);

        function resize() {
            const width = host.clientWidth;
            const height = host.clientHeight;
            if (!width || !height) return;
            const aspect = width / height;
            const size = width < 700 ? 4.5 : 4.7;
            camera.left = -size * aspect;
            camera.right = size * aspect;
            camera.top = size;
            camera.bottom = -size;
            camera.updateProjectionMatrix();
            camera.updateMatrixWorld();
            right.setFromMatrixColumn(camera.matrixWorld, 0);
            coreAssembly.position.copy(right).multiplyScalar(width < 700 ? .4 : size * aspect * .48);
            renderer.setSize(width, height);
            render();
        }

        function render() {
            corePackets.forEach(packet => packet.mesh.position.copy(packet.curve.getPointAt((elapsed * .16 + packet.offset) % 1)));
            core.rotation.y = elapsed * .28;
            coreWire.rotation.y = -elapsed * .19;
            coreRings.forEach((ring, index) => ring.rotation.z = index * .45 + elapsed * .047 * (index + 1));
            coreAssembly.rotation.y += (.08 + pointerX * .14 - coreAssembly.rotation.y) * .04;
            coreAssembly.rotation.x += (pointerY * .025 - coreAssembly.rotation.x) * .04;
            renderer.render(scene, camera);
        }

        function tick(now) {
            frame = 0;
            if (!visible || paused || scrolling || document.hidden) return;
            if (now - last >= 32) {
                elapsed += Math.min((now - last) / 1000, .05);
                last = now;
                render();
            }
            frame = requestAnimationFrame(tick);
        }

        function schedule() {
            if (frame) cancelAnimationFrame(frame);
            frame = 0;
            last = performance.now();
            if (!paused && visible && !scrolling && !document.hidden) frame = requestAnimationFrame(tick);
        }

        document.querySelector('.intro').addEventListener('pointermove', event => {
            if (motionPreference.matches || paused) return;
            const rect = host.getBoundingClientRect();
            pointerX = (event.clientX - rect.left) / rect.width - .5;
            pointerY = (event.clientY - rect.top) / rect.height - .5;
        }, { passive: true });
        motionPreference.addEventListener('change', event => { paused = event.matches; schedule(); });
        document.addEventListener('visibilitychange', schedule);
        addEventListener('scroll', () => {
            scrolling = true;
            schedule();
            clearTimeout(scrollTimer);
            scrollTimer = setTimeout(() => {
                scrolling = false;
                schedule();
            }, 120);
        }, { passive: true });
        new IntersectionObserver(entries => { visible = entries[0].isIntersecting; schedule(); }).observe(host);
        new ResizeObserver(resize).observe(host);
        renderer.domElement.addEventListener('webglcontextlost', event => {
            event.preventDefault();
            paused = true;
            schedule();
            host.classList.remove('scene-ready');
        });
        resize();
        host.classList.add('scene-ready');
        schedule();
    } catch (error) {
        host.classList.remove('scene-ready');
        console.warn('Vista estática de la portada:', error.message);
    }
}
