        if not results:
            empty_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, padx=20, pady=50)
            
            empty_label = ctk.CTkLabel(
                empty_frame,
                text=f"No movies found for '{search_query}'",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            empty_label.pack(pady=10)
            
            suggestion_label = ctk.CTkLabel(
                empty_frame,
                text="Try a different search term",
                font=ctk.CTkFont(size=14),
                text_color="gray70"
            )
            suggestion_label.pack(pady=5)
            return 