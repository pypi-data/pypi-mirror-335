from datetime import datetime
import gradio as gr

def DalleWebUI(client, host: str = None, port: int = None, browser: bool = True, upload_size: str = "4MB",
               public: bool = False, limit: int = 1, quiet: bool = False):
    """
    Start Dalle Generator Web UI with all features.
    
    Parameters:
    - client (Client): Dalle Generator instance
    - host (str): Server host
    - port (int): Server port
    - browser (bool): Launch browser automatically
    - upload_size (str): Maximum file size for uploads
    - public (bool): Enable public URL mode
    - limit (int): Maximum number of concurrent requests
    - quiet (bool): Enable quiet mode
    """
    try:        
        system_theme = gr.themes.Default(
            primary_hue=gr.themes.colors.rose,
            secondary_hue=gr.themes.colors.rose,
            neutral_hue=gr.themes.colors.zinc
        )
        
        css = '''
        ::-webkit-scrollbar {
            display: none;
        }

        ::-webkit-scrollbar-button {
            display: none;
        }

        body {
            background-color: #000000;
            background-image: linear-gradient(45deg, #111111 25%, #000000 25%, #000000 50%, #111111 50%, #111111 75%, #000000 75%, #000000 100%);
            background-size: 40px 40px;
            -ms-overflow-style: none;
        }

        gradio-app {
            --body-background-fill: None;
        }
        footer {
            display: none !important;
        }

        .app.svelte-182fdeq.svelte-182fdeq {
            padding: 0px;
        }

        .grid-wrap.svelte-hpz95u.svelte-hpz95u {
            overflow-y: auto;
        }


        .image-frame.svelte-rrgd5g img {
            object-fit: contain;
        }

        .image-container.svelte-1l6wqyv {
            height: 100%;
        }

        .grid-container.svelte-eynlr2.svelte-eynlr2 {
            grid-template-rows: repeat(auto-fit, minmax(200px, 1fr));
            grid-template-columns: repeat(auto-fit, minmax(200px, 0.505fr));
        }

        .wrap.svelte-1sbaaot {
            align-items: inherit;
        }

        .wrap.svelte-z7cif2.svelte-z7cif2 {
            z-index: 100;
            max-height: 100%;
        }

        .stage-wrap.svelte-1sbaaot {
            transform: translate(0px, 266px);
        }

        button.svelte-1uw5tnk {
            margin-bottom: 8px;
            width: 192px;
            padding: 8px;
            border-radius: var(--container-radius);
        }

        .selected.svelte-1uw5tnk {
            background: var(--button-cancel-background-fill);
            color: var(--button-cancel-text-color);
            border-radius: 10px;
            border: none;
            position: relative;
            overflow: hidden;
        }

        .tab-nav.svelte-1uw5tnk {
            justify-content: space-evenly;
            border: 0px;
        }

        div.svelte-19hvt5v {
            border-radius: 10px;
            margin-top: 12px;
            border: 1px solid var(--border-color-primary);
        }

        input[type=range].svelte-pc1gm4 {
            background-image: linear-gradient(var(--color-accent), var(--color-accent));
        }

        .thumbnails.svelte-eynlr2.svelte-eynlr2 {
            align-items: center;
            gap: 10px;
            padding-left: 10px;
            padding-right: 10px;
        }

        .icon.svelte-1oiin9d {
            display: none;
        }

        .caption-label.svelte-eynlr2.svelte-eynlr2 {
            display: none;
        }

        input[type=number].svelte-pjtc3.svelte-pjtc3 {
            line-height: 0px;
        }
        
        /* Touch device optimizations */
        @media (hover: none) {
            button, input, select {
                min-height: 44px;
            }
        }

        /* Prevent zoom on input focus for iOS */
        @media screen and (-webkit-min-device-pixel-ratio: 0) { 
            select,
            textarea,
            input {
                font-size: 16px;
            }
        }
        '''
                
        def Markdown(name:str):
            return gr.Markdown(f"{name}")

        def Textbox(name:str, lines:int=1, max_lines:int=4):
            return gr.Textbox(placeholder=f"{name}", lines=lines, max_lines=max_lines, container=False)

        def Button(name:str, variant:str='secondary'):
            return gr.Button(name, variant=variant, min_width=96)

        def Gallery(height:int):
            return gr.Gallery(height=height, object_fit="contain", container=False, show_share_button=False)

        def State(name:list):
            return gr.State(name)

        def truncate_prompt(prompt, max_length=50):
            if prompt is None or prompt == "": return "No Prompt"
            return (prompt[:max_length] + '...') if len(prompt) > max_length else prompt
        
        with gr.Blocks(title=f"Dalle Generator", css=css, analytics_enabled=False, theme=system_theme, fill_height=True).queue(default_concurrency_limit=limit) as demo:
            
            with gr.Row():
                with gr.Column(scale=1):
                    Markdown(f"## <br><center>Dalle Generator Web UI")
                    Markdown(f"<center>Copyright (C) 2025 Ikmal Said. All rights reserved")
            
            with gr.Tab("Dalle Generator"):
                
                def preprocess(pro, ram):
                    caption = f"{truncate_prompt(pro)}"
                    results = client.image_generate(pro)
                    if results is not None:
                        for img in reversed(results):
                            ram.insert(0, (img, caption))
                    return ram
                
                with gr.Row(equal_height=False):
                    with gr.Column(variant="panel", scale=1) as menu:
                        Markdown(f"## <center>Dalle Generator")
                        Markdown("<center>Basic Settings")
                        pro = Textbox("Prompt for image...", 5, 5)
                        sub = Button("Generate", "stop")
                    
                    with gr.Column(variant="panel", scale=3) as result:
                        res = Gallery(825)
                        ram = State([])
                        sub.click(
                            show_progress='minimal',
                            show_api=False,
                            scroll_to_output=True,
                            fn=preprocess,
                            inputs=[pro, ram],
                            outputs=[res]
                        )

            Markdown("<center>Dalle can make mistakes. Check important info. Request errors will return None.")
            Markdown("<center>")

        demo.launch(
            server_name=host,
            server_port=port,
            inbrowser=browser,
            max_file_size=upload_size,
            share=public,
            quiet=quiet
        )
        
    except Exception as e:
        client.logger.error(f"{str(e)}")
        raise