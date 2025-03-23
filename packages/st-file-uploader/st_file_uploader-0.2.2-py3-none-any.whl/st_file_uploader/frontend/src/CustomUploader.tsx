import React, { ReactNode } from "react";
import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib";
import { MdOutlineCloudUpload } from 'react-icons/md';
import { RxCross2 } from "react-icons/rx";
import { FaRegFile } from 'react-icons/fa';
import * as MaterialIcons from 'react-icons/md';
import * as FeatherIcons from 'react-icons/fi';
import * as FontAwesomeIcons from 'react-icons/fa';

interface State {
  files: File[] | null;
  buttonHover: boolean;
  deleteButtonHover: boolean;
  dragOver: boolean;
  processingFiles: boolean;
  hoverDeleteIndex: number | null;
  // Add a key to force input re-rendering
  fileInputKey: number;
  instanceId: string;
}

// Get icon component dynamically from icon string
function getIconComponent(iconName: string): React.ReactElement | null {
  if (!iconName) return null;
  
  // Handle different icon libraries
  if (iconName.startsWith('Md')) {
    const IconComponent = (MaterialIcons as any)[iconName];
    return IconComponent ? <IconComponent size={36} /> : <MdOutlineCloudUpload size={36} />;
  } else if (iconName.startsWith('Fi')) {
    const IconComponent = (FeatherIcons as any)[iconName];
    return IconComponent ? <IconComponent size={36} /> : <MdOutlineCloudUpload size={36} />;
  } else if (iconName.startsWith('Fa')) {
    const IconComponent = (FontAwesomeIcons as any)[iconName];
    return IconComponent ? <IconComponent size={36} /> : <MdOutlineCloudUpload size={36} />;
  }
  
  // Default to MdOutlineCloudUpload
  return <MdOutlineCloudUpload size={36} />;
}

function hexToRgb(hex: string): { r: number, g: number, b: number } {
  // Remove #
  hex = hex.replace(/^#/, '');

  // Convert hex to RGB
  var bigint = parseInt(hex, 16);
  var r = (bigint >> 16) & 255;
  var g = (bigint >> 8) & 255;
  var b = bigint & 255;

  // Return RGB values
  return { r: r, g: g, b: b };
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const formattedSize = parseFloat((bytes / Math.pow(k, i)).toFixed(2));
  return `${formattedSize} ${sizes[i]}`;
}

class CustomFileUploader extends StreamlitComponentBase<State> {
  private fileInputRef: React.RefObject<HTMLInputElement>;
  
  constructor(props: any) {
    super(props);
    this.fileInputRef = React.createRef<HTMLInputElement>();
    // Ensure each component instance has a unique ID
    this.state = {
      files: null,
      buttonHover: false,
      deleteButtonHover: false,
      dragOver: false,
      processingFiles: false,
      hoverDeleteIndex: null,
      fileInputKey: Math.random(), // More randomized key initialization
      instanceId: `file-uploader-${Date.now()}-${Math.random()}` // Add a unique instance ID
    };
  }
  
  public render = (): ReactNode => {
    const { theme } = this.props;
    const disabled = this.props.args["disabled"] || false;
    const label = this.props.args["label"] || "Upload file";
    const acceptMultipleFiles = this.props.args["acceptMultipleFiles"] || false;
    const uploaderMsg = this.props.args["uploaderMsg"] || "Drag and drop file here";
    const limitMsg = this.props.args["limitMsg"] || `Limit ${this.props.args["maxUploadSize"] || 200} MB per file`;
    const buttonMsg = this.props.args["buttonMsg"] || "Browse files";
    const iconName = this.props.args["icon"] || "MdOutlineCloudUpload";
    const fileType = this.props.args["type"] || null;
    let acceptedExtensions: string[] = [];
    if (fileType) {
      if (Array.isArray(fileType)) {
        acceptedExtensions = fileType.map(type => `.${type}`);
      } else {
        acceptedExtensions = [`.${fileType}`];
      }
    }    
    // Set label visibility
    const labelVisibility = this.props.args["labelVisibility"] || "visible";
    const label_style: React.CSSProperties = {
      visibility: labelVisibility === "visible" ? "visible" : "hidden",
      fontSize: "14px",
      display: "flex",
      marginBottom: "0.25rem",
      height: "auto",
      minHeight: "1.5rem",
      verticalAlign: "middle",
      flexDirection: "row",
      WebkitBoxAlign: "center",
      alignItems: "center",
      color: theme?.textColor,
    };

    // Form style
    const form_style: React.CSSProperties = {
      display: "flex",
      WebkitBoxAlign: "center",
      alignItems: "center",
      padding: "1rem",
      borderRadius: "0.5rem",
      cursor: this.state.processingFiles || disabled ? "not-allowed" : "pointer",
      color: theme?.textColor,
      backgroundColor: theme?.secondaryBackgroundColor,
      border: this.state.dragOver ? `1px dashed ${theme?.primaryColor}` : "none",
      pointerEvents: this.state.processingFiles ? "none" : "auto"
    };
    
    // Button style
    const browse_btn_style: React.CSSProperties = {
      display: "inline-flex",
      WebkitBoxAlign: "center",
      alignItems: "center",
      WebkitBoxPack: "center",
      justifyContent: "center",
      fontWeight: 400,
      padding: "0.25rem 0.75rem",
      borderRadius: "0.5rem",
      minHeight: "38.4px",
      margin: "0px",
      lineHeight: "1.6",
      color: "inherit",
      width: "auto",
      userSelect: "none",
      backgroundColor: theme?.backgroundColor,
      cursor: "pointer",
      fontSize: "0.875rem",
    };
    
    if (disabled) {
      browse_btn_style.opacity = 0.4;
      browse_btn_style.cursor = "not-allowed";
    }
    
    if (this.state.buttonHover) {
      // Apply hover style
      browse_btn_style.border = `1px solid ${theme?.primaryColor}`;
      browse_btn_style.color = theme?.primaryColor;
    } else {
      // Convert hex to rgb and set opacity to 0.6
      const hex = theme?.textColor as string;
      const { r, g, b } = hexToRgb(hex);
      browse_btn_style.border = `1px solid rgba(${r}, ${g}, ${b}, 0.2)`;
      browse_btn_style.color = theme?.textColor;
    }

    const delete_btn_style: React.CSSProperties = {
      display: "inline-flex",
      WebkitBoxAlign: "center",
      alignItems: "center",
      WebkitBoxPack: "center",
      justifyContent: "center",
      fontWeight: 400,
      borderRadius: "0.5rem",
      minHeight: "38.4px",
      margin: "0px",
      lineHeight: "1.6",
      width: "auto",
      userSelect: "none",
      backgroundColor: "transparent",
      border: "none",
      boxShadow: "none",
      padding: "0px",
      cursor: "pointer",
    };
    
    if (this.state.deleteButtonHover) {
      // Apply hover style
      delete_btn_style.color = theme?.primaryColor;
    } else {
      delete_btn_style.color = theme?.textColor;
    }

    // Prepare the accept attribute for file input
    let acceptTypes = "*/*";
    if (fileType) {
      if (Array.isArray(fileType)) {
        acceptTypes = fileType.map(type => `.${type}`).join(',');
      } else {
        acceptTypes = `.${fileType}`;
      }
    }
    
    return (
      <main style={{ fontFamily: theme?.font }}>
        {labelVisibility !== "collapsed" && (
          <p style={label_style}>{label}</p>
        )}
        
        <form 
          style={form_style}
          onClick={() => {
            if (!disabled) this.fileInputRef.current?.click();
          }}
          onDragOver={(e) => this.onDragOver(e)}
          onDragEnter={() => this.setState({ dragOver: true })}
          onDragLeave={() => this.setState({ dragOver: false })}
          onDrop={(e) => {
            this.onDrop(e);
            this.setState({ dragOver: false });
          }}
        >
          <input
            type="file"
            accept={acceptTypes}
            ref={this.fileInputRef}
            key={`file-input-${this.state.fileInputKey}`} // Add key for forcing re-render
            hidden
            multiple={acceptMultipleFiles}
            onClick={(e) => {
              e.stopPropagation();
            }}
            onChange={this.onFileChange}
            disabled={disabled}
          />
          
          <div style={{
            display: "flex",
            alignItems: "center",
            WebkitBoxAlign: "center",
            marginRight: "auto",
          }}>
            <span style={{ marginRight: "1rem", color: theme?.textColor, opacity: 0.6 }}>
              {getIconComponent(iconName)}
            </span>
            <div style={{ display: "flex", flexDirection: "column" }}>
              <span style={{
                fontSize: "0.875rem",
                marginBottom: "0.25rem",
                opacity: disabled ? 0.6 : 1,
              }}>{uploaderMsg}</span>
              <small style={{
                color: theme?.textColor,
                opacity: 0.6,
              }}>
                {limitMsg}
                {acceptedExtensions.length
                  ? ` • ${acceptedExtensions
                      .map(ext => ext.replace(/^\./, "").toUpperCase())
                      .join(", ")}`
                  : null}
              </small>            
            </div>
          </div>
          
          <button 
            type="button" 
            style={browse_btn_style}
            disabled={disabled}
            onMouseEnter={() => this.setState({ buttonHover: true })}
            onMouseLeave={() => this.setState({ buttonHover: false })}
          >
            {buttonMsg}
          </button>
        </form>
        
        {this.state.files && this.state.files.length > 0 && (
          <div style={{
            left: 0,
            right: 0,
            lineHeight: 1.25,
            paddingTop: "0.75rem",
          }}>
            {this.state.files.map((file, index) => (
              <div 
                key={index}
                style={{
                  display: "flex",
                  WebkitBoxAlign: "center",
                  alignItems: "center",
                  marginBottom: "0.5rem",
                  padding: "0.5rem 1rem",
                  borderRadius: "0.5rem",
                  backgroundColor: "transparent",
                }}
              >
                <div style={{
                  display: "flex",
                  padding: "0.25rem",
                  color: theme?.textColor,
                  opacity: 0.6,
                }}>
                  <FaRegFile size='1.5rem' />
                </div>
                
                <div style={{
                  display: "flex",
                  WebkitBoxAlign: "center",
                  alignItems: "center",
                  flex: "1 1 0%",
                  paddingLeft: "1rem",
                  overflow: "hidden",
                }}>
                  <div style={{
                    marginRight: "0.5rem",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap"
                  }}>
                    {file.name}
                  </div>
                  <small style={{ opacity: 0.6, lineHeight: 1.25 }}>
                    {formatBytes(file.size)}
                  </small>
                </div>
                
                <div>
                  <button 
                    type="button"
                    style={{
                      display: "inline-flex",
                      WebkitBoxAlign: "center",
                      alignItems: "center",
                      WebkitBoxPack: "center",
                      justifyContent: "center",
                      fontWeight: 400,
                      borderRadius: "0.5rem",
                      minHeight: "38.4px",
                      margin: "0px",
                      lineHeight: "1.6",
                      width: "auto",
                      userSelect: "none",
                      backgroundColor: "transparent",
                      border: "none",
                      boxShadow: "none",
                      padding: "0px",
                      cursor: "pointer",
                      color: this.state.hoverDeleteIndex === index ? theme?.primaryColor : theme?.textColor
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      this.removeFile(index);
                    }}
                    onMouseEnter={() => this.setState({ hoverDeleteIndex: index })}
                    onMouseLeave={() => this.setState({ hoverDeleteIndex: null })}
                  >
                    <RxCross2 size='1.25rem' />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    );
  };

  private onDragOver = (event: React.DragEvent<HTMLFormElement>): void => {
    event.preventDefault();
    event.stopPropagation();
  };

  private onDrop = (event: React.DragEvent<HTMLFormElement>): void => {
    event.preventDefault();
    event.stopPropagation();
    
    const { disabled } = this.props.args;
    if (disabled || this.state.processingFiles) return;
    
    const files = event.dataTransfer.files;
    if (!files || files.length === 0) return;
    
    this.setState({ processingFiles: true });
    const fileArray = Array.from(files);
    const acceptMultipleFiles = this.props.args["acceptMultipleFiles"] || false;
    
    // Simplify state handling
    this.setState({ 
        files: acceptMultipleFiles ? fileArray : [fileArray[0]],
        dragOver: false
    }, this.updateStreamlit);
  };

  private handleDrop = (files: FileList | null): void => {
    if (!files || files.length === 0) return;
    
    this.setState({ processingFiles: true }, () => {
      const fileArray = Array.from(files);
      const acceptMultipleFiles = this.props.args["acceptMultipleFiles"] || false;
      
      requestAnimationFrame(() => {
        if (acceptMultipleFiles) {
          this.setState({ files: fileArray }, () => {
            requestAnimationFrame(() => {
              this.updateStreamlit();
            });
          });
        } else {
          this.setState({ files: [fileArray[0]] }, () => {
            requestAnimationFrame(() => {
              this.updateStreamlit();
            });
          });
        }
      });
    });
  };

  private onFileChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    // Prevent file processing during handling
    this.setState({ processingFiles: true });
    
    const fileArray = Array.from(files);
    const acceptMultipleFiles = this.props.args["acceptMultipleFiles"] || false;
    
    // Create proper copies of the files
    const filesCopy = acceptMultipleFiles 
      ? fileArray.map(f => new File([f], f.name, { type: f.type, lastModified: f.lastModified })) 
      : [new File([fileArray[0]], fileArray[0].name, { type: fileArray[0].type, lastModified: fileArray[0].lastModified })];
    
    // Use requestAnimationFrame for better handling
    requestAnimationFrame(() => {
      this.setState({ 
        files: filesCopy
      }, () => {
        requestAnimationFrame(this.updateStreamlit);
      });
    });
  };

  private removeFile = (index: number): void => {
    const { files } = this.state;
    if (!files) return;
    
    const newFiles = [...files];
    newFiles.splice(index, 1);
    
    // Increment the key to force input re-rendering
    this.setState({ 
        files: newFiles.length > 0 ? newFiles : null,
        processingFiles: true,
        hoverDeleteIndex: null,
        fileInputKey: this.state.fileInputKey + 1 // Force file input re-rendering
    }, this.updateStreamlit);
  };

  private updateStreamlit = (): void => {
    const { files } = this.state;
    const acceptMultipleFiles = this.props.args["acceptMultipleFiles"] || false;
  
    if (!files || files.length === 0) {
      Streamlit.setComponentValue(acceptMultipleFiles ? [] : null);
      return;
    }
  
    // Función para leer un archivo y devolver un objeto con los datos en base64
    const readFile = (file: File): Promise<any> => {
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => {
          resolve({
            name: file.name,
            type: file.type,
            size: file.size,
            data: reader.result
          });
        };
        reader.onerror = (error) => {
          console.error("Error al leer el archivo:", error);
          // Resolver con null para evitar bloquear el procesamiento
          resolve(null);
        };
        reader.readAsDataURL(file);
      });
    };
  
    // Procesar todos los archivos y enviar el resultado a Streamlit
    Promise.all(files.map(readFile)).then((processedFiles) => {
      // Filtrar archivos nulos en caso de error de lectura
      const validFiles = processedFiles.filter(file => file !== null);
      Streamlit.setComponentValue(acceptMultipleFiles ? validFiles : validFiles[0] || null);
      this.setState({ processingFiles: false });
    });
  };  
}

export default withStreamlitConnection(CustomFileUploader);