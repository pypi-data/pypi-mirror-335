class HTTPException(Exception):
    def __init__(self, code, title, description):
        """
        Initializes a custom HTTP exception.

        :param code: HTTP status code (e.g., 404, 500)
        :param title: Error title (e.g., "Not Found")
        :param description: Error description (e.g., "The requested resource was not found.")
        """
        self.code = code
        self.title = title
        self.description = description
        super().__init__(f"{code} - {title}: {description}")

    def __str__(self):
        """
        Returns a string representation of the custom exception.
        """
        return f"HTTP Exception: {self.code} - {self.title}: {self.description}"

    def get_response(self):
        """
        Returns a dictionary with the structured HTTP response.
        """
        return {
            "code": self.code,
            "title": self.title,
            "description": self.description
        }
