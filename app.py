from flask import Flask
import logging
import time
import random
import json
import os
import schedule
from threading import Thread
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

app = Flask(__name__)

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/instagram_growth.log')
    ]
)
logger = logging.getLogger(__name__)

class UltimateInstagramBot:
    def __init__(self):
        self.setup_driver()
        self.wait = WebDriverWait(self.driver, 20)
        
        # Compte Instagram
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        
        # Objectif 10k followers en 2 mois
        self.target_followers = 10000
        self.days_to_target = 60
        self.daily_follow_target = 167  # 10k / 60 jours
        
        # Statistiques
        self.stats = {
            'total_follows': 0,
            'total_unfollows': 0,
            'daily_follows': 0,
            'daily_unfollows': 0,
            'followers_gained': 0,
            'completion_rate': 0,
            'days_remaining': 60
        }
        
        self.load_stats()
        
        logger.info("🤖 BOT INSTAGRAM ULTIME INITIALISÉ - Objectif 10k followers")

    def setup_driver(self):
        """Configuration avancée du navigateur"""
        chrome_options = Options()
        
        # Configuration Render
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Furtivité
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def login(self):
        """Connexion robuste à Instagram"""
        try:
            logger.info("🔐 CONNEXION INSTAGRAM EN COURS...")
            
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(4)

            # Accepter les cookies
            try:
                cookie_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Autoriser')]")
                cookie_button.click()
                time.sleep(2)
            except:
                pass

            # Nom d'utilisateur
            username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
            username_field.clear()
            self.slow_type(username_field, self.username)
            logger.info("📧 Username saisi")

            # Mot de passe
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            self.slow_type(password_field, self.password)
            logger.info("🔑 Mot de passe saisi")

            # Connexion
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            logger.info("🖱️ Clic connexion")

            # Attendre connexion
            time.sleep(6)

            # Sauvegarder les infos de connexion ?
            try:
                not_now_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Plus tard')]")
                not_now_button.click()
                time.sleep(2)
            except:
                pass

            # Vérifier connexion
            if "instagram.com" in self.driver.current_url and "login" not in self.driver.current_url:
                logger.info("✅ CONNECTÉ À INSTAGRAM !")
                return True
            else:
                logger.error("❌ Échec connexion Instagram")
                return False

        except Exception as e:
            logger.error(f"💥 ERREUR CONNEXION: {e}")
            return False

    def slow_type(self, element, text):
        """Taper comme un humain"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))

    def smart_follow_strategy(self, max_follows=50):
        """STRATÉGIE INTELLIGENTE DE FOLLOW"""
        try:
            logger.info(f"🎯 DÉBUT STRATÉGIE FOLLOW - Objectif: {max_follows} follows")
            
            follows_done = 0
            consecutive_failures = 0
            
            # Sources d'utilisateurs à suivre
            user_sources = [
                self.explore_hashtag_users,
                self.follow_suggested_users,
                self.follow_followers_of_similar_accounts
            ]
            
            while follows_done < max_follows and consecutive_failures < 5:
                # Choisir une stratégie aléatoire
                strategy = random.choice(user_sources)
                new_follows = strategy(min(15, max_follows - follows_done))
                
                if new_follows > 0:
                    follows_done += new_follows
                    consecutive_failures = 0
                    logger.info(f"✅ {new_follows} nouveaux follows - Total: {follows_done}")
                    
                    # Délai entre les stratégies
                    time.sleep(random.randint(20, 40))
                else:
                    consecutive_failures += 1
                    logger.info("🔍 Aucun follow réussi, changement de stratégie...")
                    time.sleep(10)

            logger.info(f"🎯 STRATÉGIE FOLLOW TERMINÉE: {follows_done} follows")
            return follows_done
            
        except Exception as e:
            logger.error(f"❌ Erreur stratégie follow: {e}")
            return 0

    def explore_hashtag_users(self, max_follows=10):
        """Suivre des utilisateurs depuis les hashtags"""
        try:
            logger.info("🏷️ Exploration hashtags...")
            
            # Hashtags de niche (À PERSONNALISER)
            hashtags = [
                "#musicproducer", "#djlife", "#edm", "#producer", "#beatmaker",
                "#housemusic", "#techno", "#dancemusic", "#electronicmusic",
                "#musicproduction", "#ableton", "#flstudio", "#musicmaker"
            ]
            
            follows_done = 0
            hashtag = random.choice(hashtags)
            
            self.driver.get(f"https://www.instagram.com/explore/tags/{hashtag[1:]}/")
            time.sleep(5)
            
            # Ouvrir un post aléatoire
            posts = self.driver.find_elements(By.XPATH, "//article//a")
            if posts:
                random_post = random.choice(posts[:9])  # Premiers 9 posts
                random_post.click()
                time.sleep(3)
                
                # Follow les utilisateurs qui ont liké/commenté
                for _ in range(max_follows):
                    if follows_done >= max_follows:
                        break
                    
                    # Voir les likes
                    try:
                        likes_link = self.driver.find_element(By.XPATH, "//a[contains(@href, 'liked_by')]")
                        likes_link.click()
                        time.sleep(3)
                        
                        # Follow des utilisateurs dans la liste
                        follow_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Follow')]")
                        
                        for button in follow_buttons[:3]:  # Max 3 par post
                            try:
                                button.click()
                                follows_done += 1
                                logger.info(f"➕ FOLLOW #{follows_done} depuis hashtag {hashtag}")
                                
                                # Délai entre follows
                                time.sleep(random.randint(12, 25))
                                
                                if follows_done >= max_follows:
                                    break
                                    
                            except:
                                continue
                                
                        # Fermer la modal
                        close_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Close']")
                        close_button.click()
                        time.sleep(2)
                        
                    except:
                        pass
                    
                    # Passer au post suivant
                    next_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Next']")
                    next_button.click()
                    time.sleep(3)

            return follows_done
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur hashtag: {e}")
            return 0

    def follow_followers_of_similar_accounts(self, max_follows=12):
        """Suivre les followers de comptes similaires"""
        try:
            logger.info("👥 Followers de comptes similaires...")
            
            # Comptes similaires dans votre niche (À PERSONNALISER)
            similar_accounts = [
                "martingarrix", "davidguetta", "arminvanbuuren", "tiesto",
                "alok", "dvlm", "hardwell", "afrojack", "nickromero"
            ]
            
            follows_done = 0
            account = random.choice(similar_accounts)
            
            self.driver.get(f"https://www.instagram.com/{account}/followers/")
            time.sleep(5)
            
            # Scroll et follow des followers
            for _ in range(3):  # 3 scrolls
                follow_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Follow')]")
                
                for button in follow_buttons[:min(4, max_follows - follows_done)]:
                    try:
                        self.driver.execute_script("arguments[0].click();", button)
                        follows_done += 1
                        logger.info(f"➕ FOLLOW #{follows_done} depuis {account}")
                        
                        time.sleep(random.randint(15, 30))
                        
                        if follows_done >= max_follows:
                            break
                            
                    except:
                        continue
                
                # Scroll pour plus de followers
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(3)
                
                if follows_done >= max_follows:
                    break

            return follows_done
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur followers similaires: {e}")
            return 0

    def follow_suggested_users(self, max_follows=10):
        """Suivre les suggestions Instagram"""
        try:
            logger.info("💡 Suggestions Instagram...")
            
            self.driver.get("https://www.instagram.com/explore/people/suggested/")
            time.sleep(5)
            
            follows_done = 0
            follow_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Follow')]")
            
            for button in follow_buttons[:max_follows]:
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    follows_done += 1
                    logger.info(f"➕ FOLLOW SUGGÉRÉ #{follows_done}")
                    
                    time.sleep(random.randint(10, 20))
                    
                except:
                    continue

            return follows_done
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur suggestions: {e}")
            return 0

    def smart_unfollow_strategy(self, max_unfollows=30):
        """STRATÉGIE INTELLIGENTE DE UNFOLLOW"""
        try:
            logger.info(f"🎯 DÉBUT STRATÉGIE UNFOLLOW - Objectif: {max_unfollows} unfollows")
            
            self.driver.get(f"https://www.instagram.com/{self.username}/following/")
            time.sleep(5)
            
            unfollows_done = 0
            consecutive_failures = 0
            
            while unfollows_done < max_unfollows and consecutive_failures < 5:
                # Trouver les boutons "Following"
                following_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Following')]")
                
                if following_buttons:
                    for button in following_buttons[:min(5, max_unfollows - unfollows_done)]:
                        try:
                            button.click()
                            time.sleep(1)
                            
                            # Confirmer l'unfollow
                            confirm_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Unfollow')]")
                            confirm_button.click()
                            
                            unfollows_done += 1
                            logger.info(f"➖ UNFOLLOW #{unfollows_done}")
                            
                            time.sleep(random.randint(8, 15))
                            
                        except:
                            consecutive_failures += 1
                            continue
                    
                    # Scroll pour plus d'utilisateurs
                    self.driver.execute_script("window.scrollBy(0, 400);")
                    time.sleep(3)
                else:
                    consecutive_failures += 1
                    break

            logger.info(f"🎯 STRATÉGIE UNFOLLOW TERMINÉE: {unfollows_done} unfollows")
            return unfollows_done
            
        except Exception as e:
            logger.error(f"❌ Erreur stratégie unfollow: {e}")
            return 0

    def engagement_actions(self, max_actions=15):
        """Actions d'engagement (likes, commentaires)"""
        try:
            logger.info(f"❤️ DÉBUT ENGAGEMENT - Objectif: {max_actions} actions")
            
            self.driver.get("https://www.instagram.com/")
            time.sleep(5)
            
            actions_done = 0
            
            # Scroll du feed
            for _ in range(5):
                # Trouver les posts à engager
                like_buttons = self.driver.find_elements(By.XPATH, "//span[@aria-label='Like']")
                comment_buttons = self.driver.find_elements(By.XPATH, "//textarea[@aria-label='Add a comment…']")
                
                # Likes
                for like in like_buttons[:3]:
                    if actions_done >= max_actions:
                        break
                    
                    try:
                        like.click()
                        actions_done += 1
                        logger.info(f"❤️ LIKE #{actions_done}")
                        time.sleep(random.randint(5, 12))
                    except:
                        continue
                
                # Commentaires (occasionnels)
                if random.random() < 0.2 and actions_done < max_actions:  # 20% de chance
                    try:
                        comment_box = random.choice(comment_buttons)
                        comment_box.click()
                        time.sleep(1)
                        
                        comment = random.choice([
                            "Great content! 👏", "Amazing! 🔥", "Love this! ❤️",
                            "So cool! 😍", "Awesome post! 🚀", "Incredible! 🤩"
                        ])
                        
                        comment_box.send_keys(comment)
                        time.sleep(1)
                        
                        post_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post')]")
                        post_button.click()
                        
                        actions_done += 1
                        logger.info(f"💬 COMMENTAIRE: {comment}")
                        time.sleep(random.randint(10, 20))
                        
                    except:
                        pass
                
                # Scroll pour plus de contenu
                self.driver.execute_script("window.scrollBy(0, 600);")
                time.sleep(random.randint(3, 7))
                
                if actions_done >= max_actions:
                    break

            logger.info(f"❤️ ENGAGEMENT TERMINÉ: {actions_done} actions")
            return actions_done
            
        except Exception as e:
            logger.error(f"❌ Erreur engagement: {e}")
            return 0

    def load_stats(self):
        """Charger les statistiques"""
        try:
            with open('/tmp/instagram_stats.json', 'r') as f:
                loaded_stats = json.load(f)
                self.stats.update(loaded_stats)
        except FileNotFoundError:
            self.save_stats()

    def save_stats(self):
        """Sauvegarder les statistiques"""
        try:
            with open('/tmp/instagram_stats.json', 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.warning(f"Stats save: {e}")

    def update_stats(self, follows=0, unfollows=0):
        """Mettre à jour les statistiques"""
        self.stats['total_follows'] += follows
        self.stats['total_unfollows'] += unfollows
        self.stats['daily_follows'] += follows
        self.stats['daily_unfollows'] += unfollows
        
        # Calcul du taux de completion
        total_done = self.stats['total_follows'] - self.stats['total_unfollows']
        self.stats['followers_gained'] = total_done
        self.stats['completion_rate'] = (total_done / self.target_followers) * 100
        self.stats['days_remaining'] = self.days_to_target - ((datetime.now() - self.get_start_date()).days)
        
        self.save_stats()

    def get_start_date(self):
        """Date de début de la campagne"""
        return datetime.now() - timedelta(days=60 - self.stats['days_remaining'])

    def close(self):
        """Fermer le navigateur"""
        try:
            self.driver.quit()
            logger.info("🔚 Navigateur fermé")
        except:
            pass

class InstagramGrowthBot:
    def __init__(self):
        self.stats = {
            'total_follows': 0,
            'total_unfollows': 0,
            'daily_follows': 0,
            'daily_unfollows': 0,
            'followers_gained': 0,
            'completion_rate': 0,
            'days_remaining': 60,
            'status': 'GROWTH_BOT_READY'
        }
        
        self.load_stats()
        
        # Configuration croissance 10k en 2 mois
        self.config = {
            'daily_follow_target': 167,
            'daily_unfollow_target': 100,
            'max_follows_per_session': 50,
            'max_unfollows_per_session': 30,
            'engagement_actions_per_session': 20
        }

    def load_stats(self):
        try:
            with open('/tmp/instagram_stats.json', 'r') as f:
                loaded_stats = json.load(f)
                self.stats.update(loaded_stats)
        except FileNotFoundError:
            self.save_stats()

    def save_stats(self):
        try:
            with open('/tmp/instagram_stats.json', 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.warning(f"Stats save: {e}")

    def is_active_time(self):
        """🕒 UNIQUEMENT PAUSE 13h-15h - Actif le reste du temps !"""
        now = datetime.now()
        current_hour = now.hour
        
        # 🕒 UNIQUEMENT PAUSE DÉJEUNER (13h-15h)
        if 13 <= current_hour < 15:
            logger.info("🍽️ PAUSE DÉJEUNER - Bot en pause 13h-15h")
            return False
        
        # ✅ ACTIF TOUT LE RESTE DU TEMPS !
        logger.info("🎯 HEURE D'ACTIVITÉ - Bot actif")
        return True

    def safety_check(self):
        """Vérifications de sécurité"""
        if not self.is_active_time():
            return False
        
        # Vérifier les limites quotidiennes
        if self.stats['daily_follows'] >= self.config['daily_follow_target']:
            logger.warning(f"🚨 Limite follows quotidienne atteinte: {self.stats['daily_follows']}")
            return False
        
        return True

    def reset_daily_counters(self):
        """Reset des compteurs quotidiens"""
        now = datetime.now()
        if 'last_daily_reset' not in self.stats:
            self.stats['last_daily_reset'] = now.isoformat()
            self.save_stats()
            return
        
        last_reset = datetime.fromisoformat(self.stats['last_daily_reset'])
        if (now - last_reset).days >= 1:
            self.stats['daily_follows'] = 0
            self.stats['daily_unfollows'] = 0
            self.stats['last_daily_reset'] = now.isoformat()
            self.save_stats()
            logger.info("🔄 Compteurs quotidiens reset")

    def growth_session(self):
        """SESSION COMPLÈTE DE CROISSANCE"""
        logger.info("🚀 DÉMARRAGE SESSION CROISSANCE INSTAGRAM")
        
        if not self.safety_check():
            logger.info("⏰ Session annulée (pause déjeuner 13h-15h)")
            return {'follows': 0, 'unfollows': 0, 'engagement': 0}
            
        self.reset_daily_counters()
        
        bot = UltimateInstagramBot()
        results = {'follows': 0, 'unfollows': 0, 'engagement': 0}
        
        try:
            if not bot.login():
                return results
            
            time.sleep(3)
            
            # 1. FOLLOW STRATÉGY
            if self.stats['daily_follows'] < self.config['daily_follow_target']:
                remaining_follows = self.config['daily_follow_target'] - self.stats['daily_follows']
                follows = bot.smart_follow_strategy(
                    max_follows=min(self.config['max_follows_per_session'], remaining_follows)
                )
                results['follows'] = follows
                bot.update_stats(follows=follows)
            
            time.sleep(random.randint(30, 60))
            
            # 2. UNFOLLOW STRATÉGY (si nécessaire)
            if random.random() < 0.6:  # 60% de chance de unfollow
                unfollows = bot.smart_unfollow_strategy(
                    max_unfollows=self.config['max_unfollows_per_session']
                )
                results['unfollows'] = unfollows
                bot.update_stats(unfollows=unfollows)
            
            time.sleep(random.randint(20, 40))
            
            # 3. ENGAGEMENT ACTIONS
            engagement = bot.engagement_actions(
                max_actions=self.config['engagement_actions_per_session']
            )
            results['engagement'] = engagement
            
            logger.info(f"🎯 SESSION CROISSANCE TERMINÉE: {results}")
            return results
            
        except Exception as e:
            logger.error(f"💥 ERREUR SESSION: {e}")
            return results
        finally:
            bot.close()

    def get_detailed_stats(self):
        """Statistiques détaillées"""
        return {
            'target_followers': 10000,
            'current_followers_gained': self.stats['followers_gained'],
            'completion_rate': round(self.stats['completion_rate'], 2),
            'days_remaining': self.stats['days_remaining'],
            'total_follows': self.stats['total_follows'],
            'total_unfollows': self.stats['total_unfollows'],
            'daily_follows': self.stats['daily_follows'],
            'daily_unfollows': self.stats['daily_unfollows'],
            'daily_follow_target': self.config['daily_follow_target'],
            'active_time': self.is_active_time(),
            'status': self.stats['status'],
            'projection_10k': f"{self.stats['days_remaining']} jours restants",
            'pause_horaire': "13h-15h uniquement"
        }

# Routes Flask
@app.route('/')
def home():
    return """
    🚀 INSTAGRAM GROWTH BOT - OBJECTIF 10K
    <br>🎯 Cible: 10,000 followers en 60 jours
    <br>📈 Suivis quotidiens: 167 | Désabonnements: 100
    <br>🕒 Activité: 24h/24 SAUF 13h-15h
    <br>🛑 UNIQUEMENT Pause: 13h-15h (déjeuner)
    <br>🌟 Stratégie: Follow/Unfollow intelligent
    <br><a href="/stats">📊 Voir la progression</a>
    <br><a href="/start-now">🚀 Démarrer maintenant</a>
    <br><a href="/strategy">🎯 Voir la stratégie</a>
    """

@app.route('/stats')
def stats():
    bot = app.config.get('bot')
    if bot:
        return bot.get_detailed_stats()
    return {"status": "ready", "message": "Bot croissance prêt - Utilisez /start-now"}

@app.route('/health')
def health():
    return {"status": "healthy", "service": "instagram_growth_bot", "timestamp": datetime.now().isoformat()}

@app.route('/start-now')
def start_now():
    """Démarrer le bot croissance immédiatement"""
    try:
        logger.info("🎯 DÉMARRAGE MANUEL BOT CROISSANCE DEMANDÉ")
        
        bot = InstagramGrowthBot()
        
        if not bot.is_active_time():
            return {
                "status": "paused", 
                "message": "⏰ Bot en pause déjeuner (13h-15h). Actif tout le reste du temps!"
            }
        
        results = bot.growth_session()
        app.config['bot'] = bot
        
        return {
            "status": "success",
            "results": results,
            "message": f"✅ Bot croissance démarré! {results['follows']} follows, {results['unfollows']} unfollows, {results['engagement']} engagements",
            "daily_progress": f"{bot.stats['daily_follows']}/{bot.config['daily_follow_target']} follows aujourd'hui"
        }
            
    except Exception as e:
        logger.error(f"❌ Erreur démarrage: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/strategy')
def show_strategy():
    """Afficher la stratégie de croissance"""
    strategy_info = {
        "objectif": "10,000 followers en 60 jours",
        "stratégie_quotidienne": {
            "follows": "167 par jour",
            "unfollows": "100 par jour", 
            "engagement": "20 actions par session"
        },
        "plannings_horaires": {
            "activité": "24H/24 SAUF 13h-15h",
            "pause_unique": "13h-15h (déjeuner)",
            "sessions_quotidiennes": "6 sessions réparties"
        },
        "sources_de_croissance": [
            "Hashtags de niche (musicproducer, djlife, edm)",
            "Followers de comptes similaires (DJs populaires)", 
            "Suggestions Instagram"
        ],
        "planning_quotidien": [
            "00:30 - Session nuit",
            "06:00 - Session matin", 
            "09:30 - Session avant-midi",
            "16:00 - Session après-pause",
            "19:30 - Session soir",
            "22:30 - Session nuit"
        ],
        "taux_de_conversion_estimé": "15-25%",
        "projection": "10K followers en 60 jours avec consistence"
    }
    return strategy_info

class GrowthScheduler:
    def __init__(self):
        self.bot = None
        self.is_running = True
    
    def initialize_bot(self):
        """Initialiser le bot croissance"""
        try:
            logger.info("🎯 INITIALISATION BOT CROISSANCE INSTAGRAM...")
            self.bot = InstagramGrowthBot()
            
            logger.info("✅ BOT CROISSANCE INITIALISÉ!")
            app.config['bot'] = self.bot
                
            if self.bot.is_active_time():
                logger.info("🚀 DÉMARRAGE SESSION IMMÉDIATE...")
                Thread(target=self.run_growth_session, daemon=True).start()
            else:
                logger.info("⏰ Pause déjeuner 13h-15h - Session différée")
            
            return True
                
        except Exception as e:
            logger.error(f"💥 ERREUR INITIALISATION: {e}")
            return False
    
    def run_growth_session(self):
        """Exécuter une session croissance"""
        if not self.bot:
            return
        
        if not self.bot.is_active_time():
            logger.info("⏰ Pause déjeuner 13h-15h - Session annulée")
            return
        
        try:
            logger.info("🎯 DÉMARRAGE SESSION CROISSANCE PROGRAMMÉE")
            results = self.bot.growth_session()
            logger.info(f"✅ Session croissance: {results}")
            
        except Exception as e:
            logger.error(f"❌ Erreur session: {e}")
    
    def start_growth_schedule(self):
        """🕒 PLANIFICATION 24H/24 SAUF 13h-15h"""
        
        # 🌙 SESSIONS NUIT (actif 24h/24 sauf 13h-15h)
        schedule.every().day.at("00:30").do(self.run_growth_session)
        schedule.every().day.at("03:00").do(self.run_growth_session)
        
        # 🌅 SESSIONS MATIN
        schedule.every().day.at("06:00").do(self.run_growth_session)
        schedule.every().day.at("09:30").do(self.run_growth_session)
        
        # 🕒 PAUSE DÉJEUNER (13h-15h) - ❌ RIEN
        
        # 🌇 SESSIONS APRÈS-MIDI
        schedule.every().day.at("16:00").do(self.run_growth_session)
        schedule.every().day.at("18:30").do(self.run_growth_session)
        
        # 🌃 SESSIONS SOIR/NUIT
        schedule.every().day.at("21:00").do(self.run_growth_session)
        schedule.every().day.at("23:30").do(self.run_growth_session)
        
        # 🔄 MAINTENANCE QUOTIDIENNE
        schedule.every().day.at("00:00").do(self.reset_daily_stats)
        
        logger.info("📅 PLANIFICATEUR 24H/24 ACTIVÉ - Pause unique 13h-15h")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(300)
    
    def reset_daily_stats(self):
        if self.bot:
            self.bot.reset_daily_counters()

def run_flask():
    """Démarrer Flask avec le bon port pour Render"""
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🌐 Démarrage serveur Flask sur le port {port}")
    logger.info(f"🚀 Application accessible sur: http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def main():
    logger.info("🚀 INSTAGRAM GROWTH BOT - OBJECTIF 10K DÉMARRAGE")
    logger.info("🕒 CONFIGURATION: Actif 24H/24 SAUF pause 13h-15h")
    
    # 🎯 INITIALISER LE BOT CROISSANCE
    scheduler = GrowthScheduler()
    app.config['scheduler'] = scheduler
    
    # DÉMARRAGE AUTOMATIQUE
    logger.info("🎯 DÉMARRAGE AUTOMATIQUE BOT CROISSANCE...")
    init_thread = Thread(target=scheduler.initialize_bot, daemon=True)
    init_thread.start()
    
    # DÉMARRER LE PLANIFICATEUR
    scheduler_thread = Thread(target=scheduler.start_growth_schedule, daemon=True)
    scheduler_thread.start()
    
    logger.info("✅ BOT CROISSANCE PRÊT - Actif 24h/24 sauf 13h-15h")
    
    # DÉMARRER FLASK
    run_flask()

if __name__ == "__main__":
    main()
