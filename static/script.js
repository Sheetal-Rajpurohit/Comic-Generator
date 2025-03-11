const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            panels: [],
            musicSource: '',
            apiUrl: 'http://localhost:5000'
        }
    },
    methods: {
        async generateComic() {
            const prompt = document.getElementById('prompt').value;
            if (!prompt) return alert('Please enter a prompt');
            
            document.getElementById('loading').classList.remove('hidden');
            document.getElementById('comic').classList.add('hidden');
            
            try {
                const response = await fetch(`${this.apiUrl}/generate-comic`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt })
                });
                
                const data = await response.json();
                
                if (data.error) throw new Error(data.error);
                
                this.panels = data.captions.map((caption, index) => ({
                    caption,
                    image: data.images[index]
                }));
                
                this.musicSource = `${this.apiUrl}/music/${data.music}`;
                document.getElementById('comic').classList.remove('hidden');
                document.getElementById('loading').classList.add('hidden');
                
                setTimeout(() => document.getElementById('musicPlayer').play(), 500);
            } catch (error) {
                console.error(error);
                alert(`Error: ${error.message}`);
            }
        }
    }
}).mount('#app');