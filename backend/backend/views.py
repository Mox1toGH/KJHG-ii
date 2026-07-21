import os
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View


class FrontendIndexView(View):
    """
    Serve the frontend index.html for client-side routing.
    This view is used for all non-API routes to let Vue Router handle the routing.
    """
    def get(self, request, *args, **kwargs):
        try:
            with open(os.path.join(settings.BASE_DIR.parent, 'frontend', 'dist', 'index.html'), 'r') as f:
                return HttpResponse(f.read(), content_type='text/html')
        except FileNotFoundError:
            # Fallback for development when frontend is not built
            return HttpResponse(
                '''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Frontend Not Built</title>
                    <style>
                        body {
                            font-family: system-ui, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: #f5f5f5;
                        }
                        .message {
                            text-align: center;
                            padding: 2rem;
                            background: white;
                            border-radius: 8px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        }
                    </style>
                </head>
                <body>
                    <div class="message">
                        <h1>Frontend Not Built</h1>
                        <p>Please build the frontend by running <code>npm run build</code> in the frontend directory.</p>
                    </div>
                </body>
                </html>
                ''',
                content_type='text/html',
                status=503
            )
