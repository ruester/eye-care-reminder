"""The app's texts in every supported language.

Same texts as the Windows app (src/windows/app/Translations.cs; the unit tests
check that both are identical). Placeholders: {0} in next_break_at and
running_message is a time of day; {0}/{1} in the default hints are counts
formatted with format_minutes / format_seconds. "&" marks the keyboard
accelerator of menu items (see mnemonic()).
"""

from dataclasses import dataclass
from typing import Tuple

from .plural import PluralRule, format_count


@dataclass(frozen=True)
class Texts:
    plural_rule: PluralRule
    minutes: Tuple[str, ...]  # counted forms "{0} minute(s)": (one, other) or (one, few, other)
    seconds: Tuple[str, ...]
    # Tray icon
    menu_settings: str
    menu_break_now: str
    menu_exit: str
    next_break_at: str
    # Settings dialog
    settings_title: str
    interval_label: str
    minutes_unit: str
    interval_default: str
    auto_hide_label: str
    seconds_unit: str
    auto_hide_default: str
    language_label: str
    test_notification: str
    save: str
    cancel: str
    # Notifications
    break_title: str
    break_message: str
    running_title: str
    running_message: str

    def format_minutes(self, count):
        return format_count(count, self.plural_rule, self.minutes)

    def format_seconds(self, count):
        return format_count(count, self.plural_rule, self.seconds)


def mnemonic(text):
    """Windows accelerator ("E&xit") -> GTK mnemonic ("E_xit")."""
    return text.replace("_", "__").replace("&", "_")


ENGLISH = Texts(
    plural_rule=PluralRule.ONE_OTHER,
    minutes=("{0} minute", "{0} minutes"),
    seconds=("{0} second", "{0} seconds"),
    menu_settings="&Settings...",
    menu_break_now="&Take a break now",
    menu_exit="E&xit",
    next_break_at="Next break at {0}",
    settings_title="Eye Care Reminder - Settings",
    interval_label="Remind me to take an eye break every:",
    minutes_unit="minutes",
    interval_default="Default: {0}",
    auto_hide_label="Hide notifications automatically after:",
    seconds_unit="seconds",
    auto_hide_default="Default: {0} (max. {1})",
    language_label="Language:",
    test_notification="Test notification",
    save="Save",
    cancel="Cancel",
    break_title="Time for an eye break",
    break_message="Look at something at least 6 meters (20 feet) away for 20 seconds and blink a few times.",
    running_title="Eye Care Reminder is running",
    running_message="Your next eye break is at {0}. Click the eye icon in the notification area to change the interval.",
)

GERMAN = Texts(
    plural_rule=PluralRule.ONE_OTHER,
    minutes=("{0} Minute", "{0} Minuten"),
    seconds=("{0} Sekunde", "{0} Sekunden"),
    menu_settings="&Einstellungen...",
    menu_break_now="&Jetzt Pause machen",
    menu_exit="&Beenden",
    next_break_at="Nächste Pause um {0}",
    settings_title="Eye Care Reminder - Einstellungen",
    interval_label="An eine Augenpause erinnern alle:",
    minutes_unit="Minuten",
    interval_default="Standard: {0}",
    auto_hide_label="Benachrichtigungen automatisch ausblenden nach:",
    seconds_unit="Sekunden",
    auto_hide_default="Standard: {0} (max. {1})",
    language_label="Sprache:",
    test_notification="Testbenachrichtigung",
    save="Speichern",
    cancel="Abbrechen",
    break_title="Zeit für eine Augenpause",
    break_message="Schauen Sie 20 Sekunden lang auf etwas, das mindestens 6 Meter entfernt ist, und blinzeln Sie ein paar Mal.",
    running_title="Eye Care Reminder läuft",
    running_message="Ihre nächste Augenpause ist um {0}. Klicken Sie auf das Augensymbol im Infobereich, um das Intervall zu ändern.",
)

FRENCH = Texts(
    plural_rule=PluralRule.FRENCH,
    minutes=("{0} minute", "{0} minutes"),
    seconds=("{0} seconde", "{0} secondes"),
    menu_settings="&Paramètres...",
    menu_break_now="&Faire une pause maintenant",
    menu_exit="&Quitter",
    next_break_at="Prochaine pause à {0}",
    settings_title="Eye Care Reminder - Paramètres",
    interval_label="Me rappeler de reposer mes yeux toutes les\u00a0:",
    minutes_unit="minutes",
    interval_default="Par défaut\u00a0: {0}",
    auto_hide_label="Masquer automatiquement les notifications après\u00a0:",
    seconds_unit="secondes",
    auto_hide_default="Par défaut\u00a0: {0} (max. {1})",
    language_label="Langue\u00a0:",
    test_notification="Tester la notification",
    save="Enregistrer",
    cancel="Annuler",
    break_title="C'est l'heure de reposer vos yeux",
    break_message="Regardez quelque chose situé à au moins 6 mètres pendant 20 secondes et clignez des yeux plusieurs fois.",
    running_title="Eye Care Reminder est lancé",
    running_message="Votre prochaine pause est à {0}. Cliquez sur l'icône de l'œil dans la zone de notification pour modifier l'intervalle.",
)

ITALIAN = Texts(
    plural_rule=PluralRule.ONE_OTHER,
    minutes=("{0} minuto", "{0} minuti"),
    seconds=("{0} secondo", "{0} secondi"),
    menu_settings="&Impostazioni...",
    menu_break_now="Fai una &pausa adesso",
    menu_exit="&Esci",
    next_break_at="Prossima pausa alle {0}",
    settings_title="Eye Care Reminder - Impostazioni",
    interval_label="Ricordami di fare una pausa per gli occhi ogni:",
    minutes_unit="minuti",
    interval_default="Predefinito: {0}",
    auto_hide_label="Nascondi automaticamente le notifiche dopo:",
    seconds_unit="secondi",
    auto_hide_default="Predefinito: {0} (max. {1})",
    language_label="Lingua:",
    test_notification="Notifica di prova",
    save="Salva",
    cancel="Annulla",
    break_title="È ora di una pausa per gli occhi",
    break_message="Guarda qualcosa ad almeno 6 metri di distanza per 20 secondi e sbatti le palpebre alcune volte.",
    running_title="Eye Care Reminder è in esecuzione",
    running_message="La prossima pausa per gli occhi è alle {0}. Fai clic sull'icona dell'occhio nell'area di notifica per modificare l'intervallo.",
)

SPANISH = Texts(
    plural_rule=PluralRule.ONE_OTHER,
    minutes=("{0} minuto", "{0} minutos"),
    seconds=("{0} segundo", "{0} segundos"),
    menu_settings="&Configuración...",
    menu_break_now="&Tomar un descanso ahora",
    menu_exit="&Salir",
    next_break_at="Próximo descanso a las {0}",
    settings_title="Eye Care Reminder - Configuración",
    interval_label="Recordarme descansar la vista cada:",
    minutes_unit="minutos",
    interval_default="Predeterminado: {0}",
    auto_hide_label="Ocultar las notificaciones automáticamente después de:",
    seconds_unit="segundos",
    auto_hide_default="Predeterminado: {0} (máx. {1})",
    language_label="Idioma:",
    test_notification="Probar notificación",
    save="Guardar",
    cancel="Cancelar",
    break_title="Hora de descansar la vista",
    break_message="Mira algo que esté al menos a 6 metros de distancia durante 20 segundos y parpadea varias veces.",
    running_title="Eye Care Reminder se está ejecutando",
    running_message="Tu próximo descanso visual es a las {0}. Haz clic en el icono del ojo en el área de notificación para cambiar el intervalo.",
)

PORTUGUESE = Texts(
    plural_rule=PluralRule.ONE_OTHER,
    minutes=("{0} minuto", "{0} minutos"),
    seconds=("{0} segundo", "{0} segundos"),
    menu_settings="&Definições...",
    menu_break_now="&Fazer uma pausa agora",
    menu_exit="&Sair",
    next_break_at="Próxima pausa às {0}",
    settings_title="Eye Care Reminder - Definições",
    interval_label="Lembrar-me de fazer uma pausa para os olhos a cada:",
    minutes_unit="minutos",
    interval_default="Predefinição: {0}",
    auto_hide_label="Ocultar as notificações automaticamente após:",
    seconds_unit="segundos",
    auto_hide_default="Predefinição: {0} (máx. {1})",
    language_label="Idioma:",
    test_notification="Testar notificação",
    save="Guardar",
    cancel="Cancelar",
    break_title="Hora de uma pausa para os olhos",
    break_message="Olhe para algo a pelo menos 6 metros de distância durante 20 segundos e pestaneje algumas vezes.",
    running_title="O Eye Care Reminder está em execução",
    running_message="A sua próxima pausa para os olhos é às {0}. Clique no ícone do olho na área de notificação para alterar o intervalo.",
)

DUTCH = Texts(
    plural_rule=PluralRule.ONE_OTHER,
    minutes=("{0} minuut", "{0} minuten"),
    seconds=("{0} seconde", "{0} seconden"),
    menu_settings="&Instellingen...",
    menu_break_now="Nu &pauze nemen",
    menu_exit="&Afsluiten",
    next_break_at="Volgende pauze om {0}",
    settings_title="Eye Care Reminder - Instellingen",
    interval_label="Herinner me aan een oogpauze om de:",
    minutes_unit="minuten",
    interval_default="Standaard: {0}",
    auto_hide_label="Meldingen automatisch verbergen na:",
    seconds_unit="seconden",
    auto_hide_default="Standaard: {0} (max. {1})",
    language_label="Taal:",
    test_notification="Testmelding",
    save="Opslaan",
    cancel="Annuleren",
    break_title="Tijd voor een oogpauze",
    break_message="Kijk 20 seconden lang naar iets dat minstens 6 meter verderop is en knipper een paar keer met je ogen.",
    running_title="Eye Care Reminder is actief",
    running_message="Je volgende oogpauze is om {0}. Klik op het oogpictogram in het systeemvak om het interval te wijzigen.",
)

NORWEGIAN = Texts(
    plural_rule=PluralRule.ONE_OTHER,
    minutes=("{0} minutt", "{0} minutter"),
    seconds=("{0} sekund", "{0} sekunder"),
    menu_settings="&Innstillinger...",
    menu_break_now="Ta en &pause nå",
    menu_exit="&Avslutt",
    next_break_at="Neste pause kl. {0}",
    settings_title="Eye Care Reminder - Innstillinger",
    interval_label="Påminnelse om øyepause med intervall på:",
    minutes_unit="minutter",
    interval_default="Standard: {0}",
    auto_hide_label="Skjul varsler automatisk etter:",
    seconds_unit="sekunder",
    auto_hide_default="Standard: {0} (maks. {1})",
    language_label="Språk:",
    test_notification="Testvarsel",
    save="Lagre",
    cancel="Avbryt",
    break_title="Tid for en øyepause",
    break_message="Se på noe som er minst 6 meter unna i 20 sekunder, og blunk noen ganger.",
    running_title="Eye Care Reminder kjører",
    running_message="Neste øyepause er kl. {0}. Klikk på øyeikonet i varslingsområdet for å endre intervallet.",
)

SWEDISH = Texts(
    plural_rule=PluralRule.ONE_OTHER,
    minutes=("{0} minut", "{0} minuter"),
    seconds=("{0} sekund", "{0} sekunder"),
    menu_settings="&Inställningar...",
    menu_break_now="Ta en &paus nu",
    menu_exit="&Avsluta",
    next_break_at="Nästa paus kl. {0}",
    settings_title="Eye Care Reminder - Inställningar",
    interval_label="Påminnelse om ögonpaus med intervallet:",
    minutes_unit="minuter",
    interval_default="Standard: {0}",
    auto_hide_label="Dölj aviseringar automatiskt efter:",
    seconds_unit="sekunder",
    auto_hide_default="Standard: {0} (max. {1})",
    language_label="Språk:",
    test_notification="Testavisering",
    save="Spara",
    cancel="Avbryt",
    break_title="Dags för en ögonpaus",
    break_message="Titta på något som är minst 6 meter bort i 20 sekunder och blinka några gånger.",
    running_title="Eye Care Reminder körs",
    running_message="Nästa ögonpaus är kl. {0}. Klicka på ögonikonen i meddelandefältet för att ändra intervallet.",
)

FINNISH = Texts(
    plural_rule=PluralRule.ONE_OTHER,
    minutes=("{0} minuutti", "{0} minuuttia"),
    seconds=("{0} sekunti", "{0} sekuntia"),
    menu_settings="&Asetukset...",
    menu_break_now="Pidä &tauko nyt",
    menu_exit="&Lopeta",
    next_break_at="Seuraava tauko klo {0}",
    settings_title="Eye Care Reminder - Asetukset",
    interval_label="Silmätauon muistutusväli:",
    minutes_unit="minuuttia",
    interval_default="Oletus: {0}",
    auto_hide_label="Piilota ilmoitukset automaattisesti, kun on kulunut:",
    seconds_unit="sekuntia",
    auto_hide_default="Oletus: {0} (enintään {1})",
    language_label="Kieli:",
    test_notification="Testi-ilmoitus",
    save="Tallenna",
    cancel="Peruuta",
    break_title="Aika pitää silmätauko",
    break_message="Katso vähintään 6 metrin päässä olevaa kohdetta 20 sekunnin ajan ja räpäytä silmiä muutaman kerran.",
    running_title="Eye Care Reminder on käynnissä",
    running_message="Seuraava silmätauko on klo {0}. Voit muuttaa väliä napsauttamalla silmäkuvaketta ilmaisinalueella.",
)

CZECH = Texts(
    plural_rule=PluralRule.CZECH,
    minutes=("{0} minuta", "{0} minuty", "{0} minut"),
    seconds=("{0} sekunda", "{0} sekundy", "{0} sekund"),
    menu_settings="&Nastavení...",
    menu_break_now="&Udělat přestávku hned",
    menu_exit="U&končit",
    next_break_at="Další přestávka v {0}",
    settings_title="Eye Care Reminder - Nastavení",
    interval_label="Interval připomenutí přestávky pro oči:",
    minutes_unit="minut",
    interval_default="Výchozí: {0}",
    auto_hide_label="Automaticky skrýt oznámení po uplynutí:",
    seconds_unit="sekund",
    auto_hide_default="Výchozí: {0} (max. {1})",
    language_label="Jazyk:",
    test_notification="Zkušební oznámení",
    save="Uložit",
    cancel="Zrušit",
    break_title="Čas na přestávku pro oči",
    break_message="Dívejte se 20 sekund na něco, co je alespoň 6 metrů daleko, a několikrát mrkněte.",
    running_title="Eye Care Reminder je spuštěný",
    running_message="Další přestávka pro oči je v {0}. Interval změníte kliknutím na ikonu oka v oznamovací oblasti.",
)

POLISH = Texts(
    plural_rule=PluralRule.POLISH,
    minutes=("{0} minuta", "{0} minuty", "{0} minut"),
    seconds=("{0} sekunda", "{0} sekundy", "{0} sekund"),
    menu_settings="&Ustawienia...",
    menu_break_now="Zrób &przerwę teraz",
    menu_exit="Za&kończ",
    next_break_at="Następna przerwa o {0}",
    settings_title="Eye Care Reminder - Ustawienia",
    interval_label="Przypominaj o przerwie dla oczu co:",
    minutes_unit="minut",
    interval_default="Domyślnie: {0}",
    auto_hide_label="Automatycznie ukrywaj powiadomienia po upływie:",
    seconds_unit="sekund",
    auto_hide_default="Domyślnie: {0} (maks. {1})",
    language_label="Język:",
    test_notification="Powiadomienie testowe",
    save="Zapisz",
    cancel="Anuluj",
    break_title="Czas na przerwę dla oczu",
    break_message="Patrz przez 20 sekund na coś oddalonego o co najmniej 6 metrów i kilka razy mrugnij.",
    running_title="Eye Care Reminder działa",
    running_message="Następna przerwa dla oczu o {0}. Kliknij ikonę oka w obszarze powiadomień, aby zmienić interwał.",
)

CROATIAN = Texts(
    plural_rule=PluralRule.CROATIAN,
    minutes=("{0} minuta", "{0} minute", "{0} minuta"),
    seconds=("{0} sekunda", "{0} sekunde", "{0} sekundi"),
    menu_settings="&Postavke...",
    menu_break_now="Napravi &stanku sada",
    menu_exit="&Izlaz",
    next_break_at="Sljedeća stanka u {0}",
    settings_title="Eye Care Reminder - Postavke",
    interval_label="Interval podsjetnika na stanku za oči:",
    minutes_unit="minuta",
    interval_default="Zadano: {0}",
    auto_hide_label="Automatski sakrij obavijesti nakon:",
    seconds_unit="sekundi",
    auto_hide_default="Zadano: {0} (najviše {1})",
    language_label="Jezik:",
    test_notification="Probna obavijest",
    save="Spremi",
    cancel="Odustani",
    break_title="Vrijeme je za stanku za oči",
    break_message="Gledajte 20 sekundi u nešto što je udaljeno najmanje 6 metara i nekoliko puta trepnite.",
    running_title="Eye Care Reminder je pokrenut",
    running_message="Sljedeća stanka za oči je u {0}. Kliknite ikonu oka u području obavijesti da biste promijenili interval.",
)
