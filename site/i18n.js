/*
  Translations of the landing page. English is the text in index.html itself
  (also shown without JavaScript); the other languages replace the content of
  every element with data-i18n="key" (HTML allowed), data-i18n-content (meta
  content) and data-i18n-aria-label. {version} is <html data-version>, the
  latest release (updated by `just bump-version`).

  Language: ?lang=xx in the URL, else the last choice in this browser, else the
  first supported browser language, else English.
*/
(function () {
  "use strict";

  var LANGUAGES = [
    { code: "de", name: "Deutschland", flag: "de" },
    { code: "en", name: "English", flag: "gb" },
    { code: "es", name: "España", flag: "es" },
    { code: "fr", name: "France", flag: "fr" },
    { code: "it", name: "Italia", flag: "it" },
  ];

  // Simplified flags (3:2), as in the Windows app.
  var FLAGS = {
    de: '<rect width="3" height="2" fill="#ffce00"/><rect width="3" height="1.333" fill="#dd0000"/><rect width="3" height=".667" fill="#000"/>',
    gb: '<rect width="3" height="2" fill="#012169"/><path d="M0 0l3 2M3 0L0 2" stroke="#fff" stroke-width=".4"/><path d="M0 0l3 2M3 0L0 2" stroke="#c8102e" stroke-width=".13"/><path d="M1.5 0v2M0 1h3" stroke="#fff" stroke-width=".667"/><path d="M1.5 0v2M0 1h3" stroke="#c8102e" stroke-width=".4"/>',
    es: '<rect width="3" height="2" fill="#aa151b"/><rect y=".5" width="3" height="1" fill="#f1bf00"/>',
    fr: '<rect width="3" height="2" fill="#ef4135"/><rect width="2" height="2" fill="#fff"/><rect width="1" height="2" fill="#0055a4"/>',
    it: '<rect width="3" height="2" fill="#ce2b37"/><rect width="2" height="2" fill="#fff"/><rect width="1" height="2" fill="#009246"/>',
  };

  var T = {
    de: {
      title: "Eye Care Reminder – regelmäßige Pausen für Ihre Augen",
      description: "Eye Care Reminder ist eine schlanke Desktop-App für Windows und Linux, die Sie in einem frei wählbaren Abstand daran erinnert, Ihre Augen auszuruhen.",
      languageLabel: "Sprache",
      navFeatures: "Funktionen",
      navDownload: "Download",
      navFaq: "FAQ",
      eyebrow: "Für alle, die am Bildschirm arbeiten",
      heroTitle: "Gönnen Sie Ihren Augen eine&nbsp;Pause.",
      heroLead: "Eye Care Reminder ist eine schlanke Desktop-App, die Sie in einem frei wählbaren Abstand daran erinnert, Ihre Augen auszuruhen – damit lange Bildschirmtage nicht mit müden, trockenen oder überanstrengten Augen enden.",
      downloadWindows: "Für Windows herunterladen",
      downloadLinux: "Für Linux herunterladen",
      heroFineprint: "Kostenlos und Open Source · Windows 10 (ab 1903), Windows 11 und Linux · Version {version}",
      toastTitle: "Zeit für eine Augenpause",
      toastMessage: "20-20-20-Regel: Schauen Sie 20 Sekunden lang auf etwas, das mindestens 6 Meter entfernt ist, und blinzeln Sie ein paar Mal.",
      featuresTitle: "Kleine App, gesunde Gewohnheit",
      featuresLead: "Sie wartet still im Infobereich und meldet sich nur, wenn es Zeit für eine Pause ist.",
      f1Title: "Ihr Rhythmus",
      f1Text: "Wählen Sie einen Abstand zwischen 1 Minute und 24 Stunden. Standardmäßig werden Sie alle 20 Minuten erinnert, nach der 20-20-20-Regel: Alle 20 Minuten für 20 Sekunden auf etwas schauen, das mindestens 6 Meter entfernt ist.",
      f2Title: "Erinnerungen, die Sie wirklich sehen",
      f2Text: "Ein deutliches Fenster unten rechts, das Ihnen nicht den Fokus stiehlt – auch bei aktiviertem „Nicht stören“.",
      f3Title: "Verschwindet von selbst",
      f3Text: "Ein Countdown-Balken zeigt, wann die Erinnerung verschwindet. Wählen Sie 1 Sekunde bis 5 Minuten oder lassen Sie sie bis zum Klick stehen.",
      f4Title: "Pause, wann es Ihnen passt",
      f4Text: "„Jetzt Pause machen“ startet sofort eine Pause, und die nächste Erinnerung zählt ab diesem Moment. Auch das Sperren des PCs zählt als Pause.",
      f5Title: "Spricht Ihre Sprache",
      f5Text: "In 13 Sprachen verfügbar und automatisch auf Ihre Systemsprache eingestellt. In den Einstellungen jederzeit umschaltbar.",
      f6Title: "Schlank und privat",
      f6Text: "Startet automatisch bei der Anmeldung und braucht kein Konto und keine Internetverbindung. Es werden keine Daten gesammelt.",
      howTitle: "So funktioniert’s",
      s1Title: "Installieren",
      s1Text: "Führen Sie das Installationsprogramm aus. Eye Care Reminder startet sofort und danach bei jeder Anmeldung.",
      s2Title: "Abstand festlegen",
      s2Text: "Klicken Sie auf das Augensymbol im Infobereich und wählen Sie, wie oft Sie erinnert werden möchten.",
      s3Title: "Wegschauen",
      s3Text: "Wenn die Erinnerung erscheint, schauen Sie 20 Sekunden lang in die Ferne und blinzeln Sie ein paar Mal.",
      downloadTitle: "Download",
      windowsRequirements: "Windows 10 (ab Version 1903) und Windows 11, 64 Bit.",
      downloadMsi: "Installationsprogramm herunterladen (.msi)",
      windowsFineprint: "Version {version}. Updates ersetzen die installierte Version automatisch.",
      linuxRequirements: "Für Xfce, Ubuntu Unity, GNOME, KDE Plasma und i3, läuft auch auf anderen Desktops. Benötigt Python 3 mit GTK 3; das Installationsprogramm bietet an, Fehlendes zu installieren.",
      downloadBin: "Installationsprogramm herunterladen (.bin)",
      linuxInstall: "Danach im Terminal in dem Ordner ausführen, in den Sie es heruntergeladen haben (ohne Root-Rechte):",
      linuxFineprint: "Version {version}. Updates ersetzen die installierte Version automatisch.",
      allReleases: 'Ältere Versionen und Versionshinweise finden Sie auf der <a href="https://github.com/ruester/eye-care-reminder/releases">Release-Seite</a>.',
      faqTitle: "Häufige Fragen",
      q1: "Windows zeigt „Der Computer wurde durch Windows geschützt“. Ist das sicher?",
      a1: "Das Installationsprogramm ist nicht mit einem kostenpflichtigen Code-Signing-Zertifikat signiert, daher warnt Microsoft Defender SmartScreen bei neuen Versionen. Klicken Sie auf <em>Weitere Informationen</em> und dann auf <em>Trotzdem ausführen</em>. Das Installationsprogramm wird aus dem öffentlichen Quellcode auf GitHub erstellt.",
      q2: "Wie ändere ich den Abstand, die Anzeigedauer oder die Sprache?",
      a2: "Klicken Sie auf das Augensymbol im Infobereich (unter Windows 11 eventuell hinter dem Pfeil <em>^</em>) oder öffnen Sie Eye Care Reminder über das Startmenü. „Testbenachrichtigung“ zeigt Ihnen eine Erinnerung mit Ihren Einstellungen.",
      q3: "Werde ich auch bei „Nicht stören“ erinnert?",
      a3: "Ja. Eye Care Reminder zeichnet seine Erinnerung selbst, statt Windows-Benachrichtigungen zu verwenden, die Windows bei „Nicht stören“ oder „Fokus“ ausblendet.",
      q4: "Wie aktualisiere oder deinstalliere ich die App?",
      a4: "Zum Aktualisieren führen Sie das neuere Installationsprogramm aus: Es ersetzt die installierte Version und behält Ihre Einstellungen. Zum Deinstallieren öffnen Sie unter Windows <em>Einstellungen → Apps → Installierte Apps</em> und entfernen Eye Care Reminder. Unter Linux führen Sie <code>sh ~/.local/share/eye-care-reminder/uninstall.sh</code> aus.",
      q5: "Welche Linux-Desktops werden unterstützt?",
      a5: "Unterstützt werden Xfce, Ubuntu Unity, GNOME, KDE Plasma und der Fenstermanager i3; das Installationsprogramm richtet ein, was der jeweilige Desktop für das Tray-Symbol braucht (z. B. die AppIndicator-Erweiterung unter GNOME). Die App läuft auch auf anderen Desktops wie Cinnamon oder MATE. Die Erinnerung kommt immer an: Kann die App ihr eigenes Popup nicht zeigen, nutzt sie die Benachrichtigungen des Desktops, notify-send oder ein einfaches Fenster. Die Einstellungen können Sie jederzeit über das Anwendungsmenü öffnen.",
      footer: 'Kostenlos und Open Source unter der <a href="https://github.com/ruester/eye-care-reminder/blob/main/LICENSE">MIT-Lizenz</a> · <a href="https://github.com/ruester/eye-care-reminder">Quellcode auf GitHub</a>',
    },
    es: {
      title: "Eye Care Reminder – descansos regulares para tu vista",
      description: "Eye Care Reminder es una aplicación de escritorio ligera para Windows y Linux que te recuerda descansar la vista con la frecuencia que elijas.",
      languageLabel: "Idioma",
      navFeatures: "Funciones",
      navDownload: "Descargar",
      navFaq: "Preguntas",
      eyebrow: "Para todos los que trabajan frente a una pantalla",
      heroTitle: "Dale un descanso a tu&nbsp;vista.",
      heroLead: "Eye Care Reminder es una aplicación de escritorio ligera que te recuerda descansar la vista con la frecuencia que elijas, para que las largas jornadas frente a la pantalla no terminen con los ojos cansados, secos o forzados.",
      downloadWindows: "Descargar para Windows",
      downloadLinux: "Descargar para Linux",
      heroFineprint: "Gratis y de código abierto · Windows 10 (1903 o posterior), Windows 11 y Linux · Versión {version}",
      toastTitle: "Hora de descansar la vista",
      toastMessage: "Regla 20-20-20: mira algo que esté al menos a 6 metros de distancia durante 20 segundos y parpadea varias veces.",
      featuresTitle: "Una pequeña app, un hábito saludable",
      featuresLead: "Espera tranquila en el área de notificación y solo aparece cuando toca descansar.",
      f1Title: "Tu ritmo",
      f1Text: "Elige cualquier intervalo entre 1 minuto y 24 horas. De forma predeterminada te avisa cada 20 minutos, según la regla 20-20-20: cada 20 minutos, mira algo que esté al menos a 6 metros durante 20 segundos.",
      f2Title: "Recordatorios que de verdad ves",
      f2Text: "Una ventana clara en la esquina inferior derecha que no te quita el foco, incluso con «No molestar» activado.",
      f3Title: "Se oculta sola",
      f3Text: "Una barra de cuenta atrás muestra cuándo desaparece el recordatorio. Elige de 1 segundo a 5 minutos o déjalo hasta que hagas clic.",
      f4Title: "Descansa cuando te venga bien",
      f4Text: "«Tomar un descanso ahora» empieza un descanso al instante y el siguiente recordatorio se cuenta desde ese momento. Bloquear el PC también cuenta como descanso.",
      f5Title: "Habla tu idioma",
      f5Text: "Disponible en 13 idiomas y configurada automáticamente en el idioma del sistema. Puedes cambiarlo cuando quieras en la configuración.",
      f6Title: "Ligera y privada",
      f6Text: "Se inicia automáticamente al iniciar sesión y no necesita cuenta ni conexión a internet. No recopila ningún dato.",
      howTitle: "Cómo funciona",
      s1Title: "Instala",
      s1Text: "Ejecuta el instalador. Eye Care Reminder se inicia al momento y, a partir de entonces, cada vez que inicias sesión.",
      s2Title: "Elige tu intervalo",
      s2Text: "Haz clic en el icono del ojo en el área de notificación para elegir cada cuánto quieres que te avise.",
      s3Title: "Aparta la vista",
      s3Text: "Cuando aparezca el recordatorio, mira algo lejano durante 20 segundos y parpadea varias veces.",
      downloadTitle: "Descargar",
      windowsRequirements: "Windows 10 (versión 1903 o posterior) y Windows 11, 64 bits.",
      downloadMsi: "Descargar instalador (.msi)",
      windowsFineprint: "Versión {version}. Las actualizaciones reemplazan automáticamente la versión instalada.",
      linuxRequirements: "Para Xfce, Ubuntu Unity, GNOME, KDE Plasma e i3; también funciona en otros escritorios. Necesita Python 3 con GTK 3; el instalador ofrece instalar lo que falte.",
      downloadBin: "Descargar instalador (.bin)",
      linuxInstall: "Después, ejecútalo en una terminal, en la carpeta donde lo descargaste (sin permisos de root):",
      linuxFineprint: "Versión {version}. Las actualizaciones reemplazan automáticamente la versión instalada.",
      allReleases: 'Las versiones anteriores y las notas de versión están en la <a href="https://github.com/ruester/eye-care-reminder/releases">página de versiones</a>.',
      faqTitle: "Preguntas frecuentes",
      q1: "Windows muestra «Windows protegió su PC». ¿Es seguro?",
      a1: "El instalador no está firmado con un certificado de firma de código de pago, por eso Microsoft Defender SmartScreen avisa mientras es nuevo. Haz clic en <em>Más información</em> y luego en <em>Ejecutar de todas formas</em>. El instalador se genera a partir del código fuente público en GitHub.",
      q2: "¿Cómo cambio el intervalo, el tiempo de ocultación o el idioma?",
      a2: "Haz clic en el icono del ojo en el área de notificación (en Windows 11 puede estar tras la flecha <em>^</em>) o abre Eye Care Reminder desde el menú Inicio. «Probar notificación» te muestra un recordatorio con tu configuración.",
      q3: "¿Me avisa aunque esté activado «No molestar»?",
      a3: "Sí. Eye Care Reminder dibuja su propio recordatorio en lugar de usar las notificaciones de Windows, que Windows oculta con «No molestar» o «Concentración».",
      q4: "¿Cómo la actualizo o la desinstalo?",
      a4: "Para actualizar, ejecuta el instalador más reciente: reemplaza la versión instalada y conserva tu configuración. Para desinstalar en Windows, ve a <em>Configuración → Aplicaciones → Aplicaciones instaladas</em> y quita Eye Care Reminder. En Linux, ejecuta <code>sh ~/.local/share/eye-care-reminder/uninstall.sh</code>.",
      q5: "¿Qué escritorios de Linux son compatibles?",
      a5: "Son compatibles Xfce, Ubuntu Unity, GNOME, KDE Plasma y el gestor de ventanas i3; el instalador configura lo que cada uno necesita para el icono de la bandeja (p. ej., la extensión AppIndicator en GNOME). La aplicación también funciona en otros escritorios como Cinnamon o MATE. El recordatorio siempre llega: si la aplicación no puede mostrar su propia ventana emergente, usa las notificaciones del escritorio, notify-send o una ventana sencilla. Siempre puedes abrir la configuración desde el menú de aplicaciones.",
      footer: 'Gratis y de código abierto con la <a href="https://github.com/ruester/eye-care-reminder/blob/main/LICENSE">licencia MIT</a> · <a href="https://github.com/ruester/eye-care-reminder">Código fuente en GitHub</a>',
    },
    fr: {
      title: "Eye Care Reminder – des pauses régulières pour vos yeux",
      description: "Eye Care Reminder est une application de bureau légère pour Windows et Linux qui vous rappelle de reposer vos yeux à l'intervalle de votre choix.",
      languageLabel: "Langue",
      navFeatures: "Fonctions",
      navDownload: "Télécharger",
      navFaq: "FAQ",
      eyebrow: "Pour tous ceux qui travaillent sur écran",
      heroTitle: "Accordez une pause à vos&nbsp;yeux.",
      heroLead: "Eye Care Reminder est une application de bureau légère qui vous rappelle de reposer vos yeux à l'intervalle de votre choix, pour que les longues journées devant l'écran ne se terminent pas avec des yeux fatigués, secs ou irrités.",
      downloadWindows: "Télécharger pour Windows",
      downloadLinux: "Télécharger pour Linux",
      heroFineprint: "Gratuit et open source · Windows 10 (1903 ou ultérieur), Windows 11 et Linux · Version {version}",
      toastTitle: "C'est l'heure de reposer vos yeux",
      toastMessage: "Règle 20-20-20 : regardez quelque chose situé à au moins 6 mètres pendant 20 secondes et clignez des yeux plusieurs fois.",
      featuresTitle: "Petite application, bonne habitude",
      featuresLead: "Elle reste discrètement dans la zone de notification et ne se manifeste que lorsqu'il est temps de faire une pause.",
      f1Title: "Votre rythme",
      f1Text: "Choisissez un intervalle de 1 minute à 24 heures. Par défaut, le rappel arrive toutes les 20 minutes, selon la règle 20-20-20 : toutes les 20 minutes, regardez quelque chose situé à au moins 6 mètres pendant 20 secondes.",
      f2Title: "Des rappels que vous voyez vraiment",
      f2Text: "Une fenêtre claire en bas à droite qui ne vous vole pas le focus, même avec « Ne pas déranger » activé.",
      f3Title: "Disparaît toute seule",
      f3Text: "Une barre de compte à rebours indique quand le rappel disparaît. Choisissez de 1 seconde à 5 minutes, ou gardez-le jusqu'à ce que vous cliquiez.",
      f4Title: "Une pause quand ça vous arrange",
      f4Text: "« Faire une pause maintenant » lance une pause immédiatement et le rappel suivant est compté à partir de ce moment. Verrouiller votre PC compte aussi comme une pause.",
      f5Title: "Parle votre langue",
      f5Text: "Disponible en 13 langues et réglée automatiquement sur la langue du système. Vous pouvez en changer à tout moment dans les paramètres.",
      f6Title: "Légère et respectueuse",
      f6Text: "Démarre automatiquement à l'ouverture de session, sans compte ni connexion Internet. Aucune donnée n'est collectée.",
      howTitle: "Comment ça marche",
      s1Title: "Installez",
      s1Text: "Lancez le programme d'installation. Eye Care Reminder démarre immédiatement, puis à chaque ouverture de session.",
      s2Title: "Choisissez l'intervalle",
      s2Text: "Cliquez sur l'icône de l'œil dans la zone de notification pour choisir la fréquence des rappels.",
      s3Title: "Regardez au loin",
      s3Text: "Quand le rappel apparaît, regardez quelque chose de lointain pendant 20 secondes et clignez des yeux plusieurs fois.",
      downloadTitle: "Télécharger",
      windowsRequirements: "Windows 10 (version 1903 ou ultérieure) et Windows 11, 64 bits.",
      downloadMsi: "Télécharger le programme d'installation (.msi)",
      windowsFineprint: "Version {version}. Les mises à jour remplacent automatiquement la version installée.",
      linuxRequirements: "Pour Xfce, Ubuntu Unity, GNOME, KDE Plasma et i3, elle fonctionne aussi sur d'autres bureaux. Nécessite Python 3 avec GTK 3 ; le programme d'installation propose d'installer ce qui manque.",
      downloadBin: "Télécharger le programme d'installation (.bin)",
      linuxInstall: "Lancez-le ensuite dans un terminal, dans le dossier où vous l'avez téléchargé (sans droits root) :",
      linuxFineprint: "Version {version}. Les mises à jour remplacent automatiquement la version installée.",
      allReleases: 'Les versions précédentes et les notes de version se trouvent sur la <a href="https://github.com/ruester/eye-care-reminder/releases">page des versions</a>.',
      faqTitle: "Questions fréquentes",
      q1: "Windows affiche « Windows a protégé votre ordinateur ». Est-ce sûr ?",
      a1: "Le programme d'installation n'est pas signé avec un certificat de signature de code payant, Microsoft Defender SmartScreen affiche donc un avertissement tant qu'il est récent. Cliquez sur <em>Informations complémentaires</em> puis sur <em>Exécuter quand même</em>. Le programme d'installation est généré à partir du code source public sur GitHub.",
      q2: "Comment modifier l'intervalle, la durée d'affichage ou la langue ?",
      a2: "Cliquez sur l'icône de l'œil dans la zone de notification (sous Windows 11, elle peut se trouver derrière la flèche <em>^</em>) ou ouvrez Eye Care Reminder depuis le menu Démarrer. « Tester la notification » affiche un rappel avec vos paramètres.",
      q3: "Suis-je rappelé même en mode « Ne pas déranger » ?",
      a3: "Oui. Eye Care Reminder affiche son propre rappel au lieu d'utiliser les notifications Windows, que Windows masque en mode « Ne pas déranger » ou « Concentration ».",
      q4: "Comment la mettre à jour ou la désinstaller ?",
      a4: "Pour la mettre à jour, lancez le nouveau programme d'installation : il remplace la version installée et conserve vos paramètres. Pour la désinstaller sous Windows, ouvrez <em>Paramètres → Applications → Applications installées</em> et supprimez Eye Care Reminder. Sous Linux, exécutez <code>sh ~/.local/share/eye-care-reminder/uninstall.sh</code>.",
      q5: "Quels bureaux Linux sont pris en charge ?",
      a5: "Xfce, Ubuntu Unity, GNOME, KDE Plasma et le gestionnaire de fenêtres i3 sont pris en charge ; le programme d'installation configure ce dont chacun a besoin pour l'icône de la zone de notification (par ex. l'extension AppIndicator sous GNOME). L'application fonctionne aussi sur d'autres bureaux comme Cinnamon ou MATE. Le rappel arrive toujours : si l'application ne peut pas afficher sa propre fenêtre contextuelle, elle utilise les notifications du bureau, notify-send ou une simple fenêtre. Vous pouvez toujours ouvrir les paramètres depuis le menu des applications.",
      footer: 'Gratuit et open source sous <a href="https://github.com/ruester/eye-care-reminder/blob/main/LICENSE">licence MIT</a> · <a href="https://github.com/ruester/eye-care-reminder">Code source sur GitHub</a>',
    },
    it: {
      title: "Eye Care Reminder – pause regolari per i tuoi occhi",
      description: "Eye Care Reminder è un'app desktop leggera per Windows e Linux che ti ricorda di far riposare gli occhi all'intervallo che scegli.",
      languageLabel: "Lingua",
      navFeatures: "Funzioni",
      navDownload: "Download",
      navFaq: "FAQ",
      eyebrow: "Per chi lavora davanti a uno schermo",
      heroTitle: "Concedi una pausa ai tuoi&nbsp;occhi.",
      heroLead: "Eye Care Reminder è un'app desktop leggera che ti ricorda di far riposare gli occhi all'intervallo che scegli, così le lunghe sessioni davanti allo schermo non finiscono con occhi stanchi, secchi o affaticati.",
      downloadWindows: "Scarica per Windows",
      downloadLinux: "Scarica per Linux",
      heroFineprint: "Gratuita e open source · Windows 10 (1903 o successivo), Windows 11 e Linux · Versione {version}",
      toastTitle: "È ora di una pausa per gli occhi",
      toastMessage: "Regola 20-20-20: guarda qualcosa ad almeno 6 metri di distanza per 20 secondi e sbatti le palpebre alcune volte.",
      featuresTitle: "Piccola app, buona abitudine",
      featuresLead: "Resta in silenzio nell'area di notifica e si fa sentire solo quando è ora di una pausa.",
      f1Title: "Il tuo ritmo",
      f1Text: "Scegli un intervallo da 1 minuto a 24 ore. Per impostazione predefinita ricevi un promemoria ogni 20 minuti, secondo la regola 20-20-20: ogni 20 minuti guarda qualcosa ad almeno 6 metri di distanza per 20 secondi.",
      f2Title: "Promemoria che vedi davvero",
      f2Text: "Una finestra chiara nell'angolo in basso a destra che non ti ruba lo stato attivo, anche con «Non disturbare» attivo.",
      f3Title: "Si nasconde da sola",
      f3Text: "Una barra di conto alla rovescia mostra quando il promemoria scompare. Scegli da 1 secondo a 5 minuti oppure lascialo finché non fai clic.",
      f4Title: "Pausa quando vuoi",
      f4Text: "«Fai una pausa adesso» avvia subito una pausa e il promemoria successivo parte da quel momento. Anche bloccare il PC conta come pausa.",
      f5Title: "Parla la tua lingua",
      f5Text: "Disponibile in 13 lingue e impostata automaticamente sulla lingua del sistema. Puoi cambiarla in qualsiasi momento nelle impostazioni.",
      f6Title: "Leggera e riservata",
      f6Text: "Si avvia automaticamente all'accesso e non richiede account né connessione a Internet. Non raccoglie alcun dato.",
      howTitle: "Come funziona",
      s1Title: "Installa",
      s1Text: "Esegui il programma di installazione. Eye Care Reminder si avvia subito e da allora in poi a ogni accesso.",
      s2Title: "Imposta l'intervallo",
      s2Text: "Fai clic sull'icona dell'occhio nell'area di notifica per scegliere ogni quanto ricevere il promemoria.",
      s3Title: "Guarda lontano",
      s3Text: "Quando appare il promemoria, guarda qualcosa di lontano per 20 secondi e sbatti le palpebre alcune volte.",
      downloadTitle: "Download",
      windowsRequirements: "Windows 10 (versione 1903 o successiva) e Windows 11, 64 bit.",
      downloadMsi: "Scarica il programma di installazione (.msi)",
      windowsFineprint: "Versione {version}. Gli aggiornamenti sostituiscono automaticamente la versione installata.",
      linuxRequirements: "Per Xfce, Ubuntu Unity, GNOME, KDE Plasma e i3, funziona anche su altri desktop. Richiede Python 3 con GTK 3; il programma di installazione si offre di installare ciò che manca.",
      downloadBin: "Scarica il programma di installazione (.bin)",
      linuxInstall: "Poi eseguilo in un terminale, nella cartella in cui l'hai scaricato (senza permessi di root):",
      linuxFineprint: "Versione {version}. Gli aggiornamenti sostituiscono automaticamente la versione installata.",
      allReleases: 'Le versioni precedenti e le note di rilascio sono nella <a href="https://github.com/ruester/eye-care-reminder/releases">pagina delle versioni</a>.',
      faqTitle: "Domande frequenti",
      q1: "Windows mostra «PC protetto da Windows». È sicuro?",
      a1: "Il programma di installazione non è firmato con un certificato di firma del codice a pagamento, quindi Microsoft Defender SmartScreen mostra un avviso finché è nuovo. Fai clic su <em>Ulteriori informazioni</em> e poi su <em>Esegui comunque</em>. Il programma di installazione è generato dal codice sorgente pubblico su GitHub.",
      q2: "Come cambio l'intervallo, il tempo di visualizzazione o la lingua?",
      a2: "Fai clic sull'icona dell'occhio nell'area di notifica (in Windows 11 potrebbe trovarsi dietro la freccia <em>^</em>) oppure apri Eye Care Reminder dal menu Start. «Notifica di prova» ti mostra un promemoria con le tue impostazioni.",
      q3: "Ricevo il promemoria anche con «Non disturbare» attivo?",
      a3: "Sì. Eye Care Reminder disegna il proprio promemoria invece di usare le notifiche di Windows, che Windows nasconde con «Non disturbare» o «Concentrazione» attivi.",
      q4: "Come la aggiorno o la disinstallo?",
      a4: "Per aggiornarla, esegui il programma di installazione più recente: sostituisce la versione installata e mantiene le tue impostazioni. Per disinstallarla su Windows, apri <em>Impostazioni → App → App installate</em> e rimuovi Eye Care Reminder. Su Linux, esegui <code>sh ~/.local/share/eye-care-reminder/uninstall.sh</code>.",
      q5: "Quali desktop Linux sono supportati?",
      a5: "Sono supportati Xfce, Ubuntu Unity, GNOME, KDE Plasma e il window manager i3; il programma di installazione configura ciò che serve a ciascuno per l'icona nell'area di notifica (ad es. l'estensione AppIndicator su GNOME). L'app funziona anche su altri desktop come Cinnamon o MATE. Il promemoria arriva sempre: se l'app non può mostrare il proprio popup, usa le notifiche del desktop, notify-send o una semplice finestra. Puoi sempre aprire le impostazioni dal menu delle applicazioni.",
      footer: 'Gratuita e open source con <a href="https://github.com/ruester/eye-care-reminder/blob/main/LICENSE">licenza MIT</a> · <a href="https://github.com/ruester/eye-care-reminder">Codice sorgente su GitHub</a>',
    },
  };

  var STORAGE_KEY = "eye-care-reminder-language";
  var root = document.documentElement;
  var version = root.getAttribute("data-version") || "";
  var english = {};

  function flagSvg(code) {
    return '<svg class="flag" viewBox="0 0 3 2" aria-hidden="true">' + FLAGS[code] + "</svg>";
  }

  function find(code) {
    code = (code || "").toLowerCase().split("-")[0];
    for (var i = 0; i < LANGUAGES.length; i++) {
      if (LANGUAGES[i].code === code) return LANGUAGES[i];
    }
    return null;
  }

  function stored() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }

  function store(code) {
    try { localStorage.setItem(STORAGE_KEY, code); } catch (e) { /* private mode */ }
  }

  function initialLanguage() {
    var fromUrl = find(new URLSearchParams(location.search).get("lang"));
    if (fromUrl) return fromUrl;
    var fromStorage = find(stored());
    if (fromStorage) return fromStorage;
    var browser = navigator.languages || [navigator.language];
    for (var i = 0; i < browser.length; i++) {
      var match = find(browser[i]);
      if (match) return match;
    }
    return find("en");
  }

  // Remember the English texts of the page so switching back needs no reload.
  function collectEnglish() {
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      english[el.getAttribute("data-i18n")] = el.innerHTML;
    });
    document.querySelectorAll("[data-i18n-content]").forEach(function (el) {
      english[el.getAttribute("data-i18n-content")] = el.getAttribute("content");
    });
    document.querySelectorAll("[data-i18n-aria-label]").forEach(function (el) {
      english[el.getAttribute("data-i18n-aria-label")] = el.getAttribute("aria-label");
    });
  }

  function text(texts, key) {
    var value = texts[key] !== undefined ? texts[key] : english[key];
    return value.replace(/\{version\}/g, version);
  }

  function apply(language) {
    var texts = T[language.code] || english;
    root.lang = language.code;
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      el.innerHTML = text(texts, el.getAttribute("data-i18n"));
    });
    document.querySelectorAll("[data-i18n-content]").forEach(function (el) {
      el.setAttribute("content", text(texts, el.getAttribute("data-i18n-content")));
    });
    document.querySelectorAll("[data-i18n-aria-label]").forEach(function (el) {
      el.setAttribute("aria-label", text(texts, el.getAttribute("data-i18n-aria-label")));
    });
    button.innerHTML = flagSvg(language.flag) + '<span class="lang-code">' + language.code.toUpperCase() + "</span>";
    menu.querySelectorAll("[role=option]").forEach(function (item) {
      item.setAttribute("aria-selected", String(item.getAttribute("data-code") === language.code));
    });
  }

  var switcher = document.querySelector(".lang-switcher");
  var button = switcher.querySelector(".lang-button");
  var menu = switcher.querySelector(".lang-menu");

  function setOpen(open) {
    menu.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
  }

  LANGUAGES.forEach(function (language) {
    var item = document.createElement("li");
    item.setAttribute("role", "option");
    item.setAttribute("data-code", language.code);
    item.setAttribute("lang", language.code);
    item.tabIndex = 0;
    item.innerHTML = flagSvg(language.flag) + "<span>" + language.name + "</span>";
    function choose() {
      store(language.code);
      apply(language);
      setOpen(false);
      button.focus();
      var url = new URL(location.href);
      if (url.searchParams.has("lang")) {
        url.searchParams.set("lang", language.code);
        history.replaceState(null, "", url);
      }
    }
    item.addEventListener("click", choose);
    item.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); choose(); }
      if (e.key === "ArrowDown" && item.nextElementSibling) { e.preventDefault(); item.nextElementSibling.focus(); }
      if (e.key === "ArrowUp" && item.previousElementSibling) { e.preventDefault(); item.previousElementSibling.focus(); }
      if (e.key === "Escape") { setOpen(false); button.focus(); }
    });
    menu.appendChild(item);
  });

  button.addEventListener("click", function () {
    var open = menu.hidden;
    setOpen(open);
    if (open) (menu.querySelector('[aria-selected="true"]') || menu.firstElementChild).focus();
  });
  document.addEventListener("click", function (e) {
    if (!switcher.contains(e.target)) setOpen(false);
  });

  collectEnglish();
  apply(initialLanguage());
  switcher.hidden = false;
})();
