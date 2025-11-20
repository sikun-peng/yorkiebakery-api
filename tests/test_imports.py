# tests/test_imports.py

def test_imports():
    # Core modules
    import app.core.db
    import app.core.cart_utils
    import app.core.security
    import app.core.send_email
    import app.core.ddb

    # Routes (your real structure)
    import app.routes.about
    import app.routes.auth
    import app.routes.menu
    import app.routes.order
    import app.routes.cart
    import app.routes.music

    # AI / RAG modules
    import app.ai.emb_model
    import app.ai.rag
    import app.ai.vecstore
    import app.ai.run_embeddings
    import app.ai.filters
    import app.ai.interpret
    import app.ai.agent_router
    import app.ai.chat_model
    import app.ai.trace_models

    # Vision + Chat AI routes — your real structure
    import app.ai.route.ai_demo
    import app.ai.route.ai_chat
    import app.ai.route.ai_vision
    import app.ai.route.ai_debug

    # Models package
    import app.models
    import app.models.postgres

    # Utilities
    import app.utils.s3_util