import gradio as gr

def KhutbahMakerWebUI(client, host: str = None, port: int = None, browser: bool = True, upload_size: str = "4MB",
                      public: bool = False, limit: int = 10, quiet: bool = True):
    """ 
    Start KhutbahMaker Web UI with all features.
    
    Parameters:
    - client (Client): KhutbahMaker instance
    - host (str): Server host
    - port (int): Server port
    - browser (bool): Launch browser automatically
    - upload_size (str): Maximum file size for uploads
    - public (bool): Enable public URL mode
    - limit (int): Maximum number of concurrent requests
    - quiet (bool): Enable quiet mode
    """
    try:
        gr_css = """
        footer {
            display: none !important;
        }
        """
        
        gr_theme = gr.themes.Default(
            primary_hue="purple",
            secondary_hue="purple",
            neutral_hue=gr.themes.colors.zinc,
            font=["Amiri", "system-ui", "sans-serif"]
        )
    
        with gr.Blocks(title="KhutbahMaker", analytics_enabled=False, theme=gr_theme, css=gr_css).queue(default_concurrency_limit=limit) as demo:
            gr.Markdown("## <br><center>KhutbahMaker Web UI")
            gr.Markdown("<center>Made for #GodamSahur 2025 by Ikmal Said")
            gr.Markdown("<center>")

            with gr.Row():
                with gr.Column():
                    with gr.Tab("Settings"):
                            with gr.Column(scale=1):
                                khutbah_topic = gr.Textbox(
                                    label="Khutbah Topic",
                                    lines=1, max_lines=1,
                                    placeholder="Type your topic here...",
                                    info="Enter the main topic or theme for the khutbah"
                                )
                                
                                khutbah_language = gr.Dropdown(
                                    value="Bahasa Malaysia", 
                                    choices=["Bahasa Malaysia", "Arabic", "English", "Mandarin", "Tamil"], 
                                    label="Khutbah Language",
                                    info="Select the language of the khutbah"
                                )
                                
                                khutbah_length = gr.Dropdown(
                                    value="Short", 
                                    choices=["Short", "Medium", "Long"], 
                                    label="Khutbah Length",
                                    info="Short (10-15 minutes), Medium (15-20 minutes) or Long (20-30 minutes)"
                                )
                                
                                khutbah_tone = gr.Dropdown(
                                    value="Scholarly", 
                                    choices=["Scholarly", "Inspirational", "Practical", "Reflective", "Motivational", "Educational", "Historical", "Narrative"], 
                                    label="Khutbah Tone",
                                    info="Select the tone of the khutbah based on the topic"
                                )
                                
                                khutbah_btn = gr.Button("Generate Khutbah", variant="primary")
                
                with gr.Column():
                    with gr.Tab("Results"):
                        with gr.Column(scale=1):
                            khutbah_output = gr.File(label="Download Khutbah as PDF")
                            with gr.Accordion("Read Khutbah as Text"):
                                khutbah_text = gr.Markdown(value="Please generate khutbah first for reading!", height=300)

            gr.Markdown("<center>")
            gr.Markdown("<center>KhutbahMaker can make mistakes. Check important info.")
            gr.Markdown("<center>")

            # Setup event handlers
            khutbah_btn.click(fn=client.generate_khutbah, inputs=[khutbah_topic, khutbah_length, khutbah_tone, khutbah_language], outputs=[khutbah_output, khutbah_text])
        
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