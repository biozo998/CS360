import logging
from flask import Blueprint, jsonify, request
from services.analytics import GovernanceAnalytics

logger = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

analytics = GovernanceAnalytics()

# === Analytics & Dashboard Routes ===

@api_bp.route("/governance/t1", methods=["GET"])
def get_governance_t1():
    try:
        data = analytics.get_t1_alerts()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        logger.error(f"API Error get_governance_t1: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route("/governance/t2", methods=["GET"])
def get_governance_t2():
    try:
        data = analytics.get_t2_alerts()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        logger.error(f"API Error get_governance_t2: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route("/governance/t3", methods=["GET"])
def get_governance_t3():
    try:
        data = analytics.get_t3_alerts()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        logger.error(f"API Error get_governance_t3: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# === Authentication Routing Logic ===
import uuid

@api_bp.route("/auth/login", methods=["POST"])
def auth_login():
    """
    Login with Email and Password.
    Returns Token if valid, checks if user exists but has no password (first access).
    """
    from database import get_db
    from models.integration import Usuario
    from services.auth import verify_password, create_access_token
    
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400
        
    db = next(get_db())
    user = db.query(Usuario).filter(Usuario.email == email).first()
    
    try:
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
            
        if user.password_hash is None:
            return jsonify({"status": "error", "message": "Generate password link required (first access)"}), 403
            
        if verify_password(password, user.password_hash):
            token_data = {"sub": user.usu_id, "email": user.email, "role": "admin"} # Role logic can be added later
            token = create_access_token(token_data)
            return jsonify({"status": "success", "token": token, "user": {"id": user.usu_id, "nome": user.nome, "email": user.email}})
        else:
            return jsonify({"status": "error", "message": "Invalid password"}), 401
    finally:
        db.close()

@api_bp.route("/auth/generate-password-link", methods=["POST"])
def auth_generate_password_link():
    """
    If user has no password, this endpoint generates a reset token and sends it.
    """
    from database import get_db
    from models.integration import Usuario
    
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400
        
    db = next(get_db())
    user = db.query(Usuario).filter(Usuario.email == email).first()
    
    try:
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
            
        # Generate token
        reset_token = str(uuid.uuid4())
        user.reset_token = reset_token
        db.commit()
        
        # Here we would integrate with an SMTP/Email service to send the link
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        logger.info(f"Password reset link generated for {email}: {reset_link}")
        
        return jsonify({"status": "success", "message": f"Link generated and ready to be sent to {email}"})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()
    
@api_bp.route("/auth/set-password", methods=["POST"])
def auth_set_password():
    """
    User clicks link, sends token and new password.
    """
    from database import get_db
    from models.integration import Usuario
    from services.auth import get_password_hash
    
    data = request.json
    token = data.get("token")
    new_password = data.get("password")
    
    if not token or not new_password:
        return jsonify({"status": "error", "message": "Token and password are required"}), 400
        
    db = next(get_db())
    user = db.query(Usuario).filter(Usuario.reset_token == token).first()
    
    try:
        if not user:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 400
            
        user.password_hash = get_password_hash(new_password)
        user.reset_token = None # Clear token after use
        db.commit()
        
        return jsonify({"status": "success", "message": "Password updated successfully"})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()
