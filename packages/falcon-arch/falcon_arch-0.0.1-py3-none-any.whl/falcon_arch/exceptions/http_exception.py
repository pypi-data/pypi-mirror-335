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
