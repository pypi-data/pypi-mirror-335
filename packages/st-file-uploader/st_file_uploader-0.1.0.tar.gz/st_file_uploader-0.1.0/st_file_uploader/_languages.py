from dataclasses import dataclass
from typing import Optional


@dataclass
class LanguagePack:
    """Language pack for customizing file uploader text."""
    uploader_msg: str  # "Drag and drop file here"
    limit_msg: str     # "Limit ... per file"
    button_msg: str    # "Browse files"
    icon: str = "MdOutlineCloudUpload"  # Default icon


class CustomLanguagePack(LanguagePack):
    """Custom language pack that allows partial overrides."""
    
    def __init__(
        self,
        uploader_msg: Optional[str] = None,
        limit_msg: Optional[str] = None,
        button_msg: Optional[str] = None,
        icon: Optional[str] = None,
    ):
        # Use English defaults for any unspecified values
        en_pack = LANGUAGE_PACKS["en"]
        super().__init__(
            uploader_msg=uploader_msg if uploader_msg is not None else en_pack.uploader_msg,
            limit_msg=limit_msg if limit_msg is not None else en_pack.limit_msg,
            button_msg=button_msg if button_msg is not None else en_pack.button_msg,
            icon=icon if icon is not None else en_pack.icon,
        )


# Language pack definitions
LANGUAGE_PACKS = {
    "en": LanguagePack(
        uploader_msg="Drag and drop file here",
        limit_msg="Limit {max_upload_size} MB per file",
        button_msg="Browse files",
    ),
    "es": LanguagePack(
        uploader_msg="Arrastra y suelta el archivo aquí",
        limit_msg="Límite de {max_upload_size} MB por archivo",
        button_msg="Buscar archivos",
    ),
    "fr": LanguagePack(
        uploader_msg="Glissez et déposez le fichier ici",
        limit_msg="Limite de {max_upload_size} MB par fichier",
        button_msg="Parcourir les fichiers",
    ),
    "de": LanguagePack(
        uploader_msg="Datei hier ablegen",
        limit_msg="Limit von {max_upload_size} MB pro Datei",
        button_msg="Dateien durchsuchen",
    ),
    "it": LanguagePack(
        uploader_msg="Trascina e rilascia il file qui",
        limit_msg="Limite di {max_upload_size} MB per file",
        button_msg="Sfoglia file",
    ),
    "pt": LanguagePack(
        uploader_msg="Arraste e solte o arquivo aqui",
        limit_msg="Limite de {max_upload_size} MB por arquivo",
        button_msg="Procurar arquivos",
    ),
    "zh": LanguagePack(
        uploader_msg="将文件拖放到这里",
        limit_msg="每个文件限制 {max_upload_size} MB",
        button_msg="浏览文件",
    ),
    "ja": LanguagePack(
        uploader_msg="ここにファイルをドラッグ＆ドロップ",
        limit_msg="ファイルあたり {max_upload_size} MB の制限",
        button_msg="ファイルを参照",
    ),
    "ko": LanguagePack(
        uploader_msg="여기에 파일을 끌어다 놓으세요",
        limit_msg="파일당 {max_upload_size} MB 제한",
        button_msg="파일 찾아보기",
    ),
    "ru": LanguagePack(
        uploader_msg="Перетащите файл сюда",
        limit_msg="Лимит {max_upload_size} MB на файл",
        button_msg="Обзор файлов",
    ),
    # Added languages
    "ar": LanguagePack(
        uploader_msg="اسحب وأفلت الملف هنا",
        limit_msg="الحد {max_upload_size} ميجابايت لكل ملف",
        button_msg="تصفح الملفات",
    ),
    "hi": LanguagePack(
        uploader_msg="फ़ाइल यहां खींचें और छोड़ें",
        limit_msg="प्रति फ़ाइल {max_upload_size} MB की सीमा",
        button_msg="फ़ाइलें ब्राउज़ करें",
    ),
    "nl": LanguagePack(
        uploader_msg="Sleep het bestand hier naartoe",
        limit_msg="Limiet van {max_upload_size} MB per bestand",
        button_msg="Bestanden zoeken",
    ),
    "sv": LanguagePack(
        uploader_msg="Dra och släpp filen här",
        limit_msg="Gräns på {max_upload_size} MB per fil",
        button_msg="Bläddra bland filer",
    ),
    "pl": LanguagePack(
        uploader_msg="Przeciągnij i upuść plik tutaj",
        limit_msg="Limit {max_upload_size} MB na plik",
        button_msg="Przeglądaj pliki",
    ),
    "tr": LanguagePack(
        uploader_msg="Dosyayı buraya sürükleyip bırakın",
        limit_msg="Dosya başına {max_upload_size} MB sınırı",
        button_msg="Dosyalara göz at",
    ),
    "he": LanguagePack(
        uploader_msg="גרור ושחרר קובץ כאן",
        limit_msg="מגבלה של {max_upload_size} MB לקובץ",
        button_msg="עיון בקבצים",
    ),
    "th": LanguagePack(
        uploader_msg="ลากและวางไฟล์ที่นี่",
        limit_msg="จำกัด {max_upload_size} MB ต่อไฟล์",
        button_msg="เรียกดูไฟล์",
    ),
    "id": LanguagePack(
        uploader_msg="Seret dan lepaskan file di sini",
        limit_msg="Batas {max_upload_size} MB per file",
        button_msg="Telusuri file",
    ),
    "vi": LanguagePack(
        uploader_msg="Kéo và thả tệp vào đây",
        limit_msg="Giới hạn {max_upload_size} MB mỗi tệp",
        button_msg="Duyệt tệp",
    ),
}