import { Component } from '@angular/core';
import { 
  IonHeader, IonToolbar, IonContent, IonButton, 
  IonGrid, IonRow, IonCol, IonCard, IonCardHeader, 
  IonCardTitle, IonCardContent, IonItem, IonInput, 
  IonTextarea, IonIcon, IonTitle } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { 
  documentTextOutline, 
  shieldCheckmarkOutline, 
  fingerPrintOutline, 
  briefcaseOutline 
} from 'ionicons/icons';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  standalone: true,
  imports: [IonTitle, 
    IonHeader, IonToolbar, IonContent, IonButton, 
    IonGrid, IonRow, IonCol, IonCard, IonCardHeader, 
    IonCardTitle, IonCardContent, IonItem, IonInput, 
    IonTextarea, IonIcon
  ],
})
export class HomePage {
  // Arreglo de servicios adaptado a Compruebame Ecofirma
  servicios = [
    { 
      icon: 'document-text-outline', 
      title: 'Firma Digital NOM-151', 
      desc: 'Conservación de mensajes de datos con validez jurídica.' 
    },
    { 
      icon: 'shield-checkmark-outline', 
      title: 'Soluciones CFDI 4.0', 
      desc: 'Servicios de timbrado, facturación y conectores web.' 
    },
    { 
      icon: 'fingerprint-outline', 
      title: 'Validación Biométrica', 
      desc: 'Verificación de identidad y seguridad en tus trámites.' 
    },
    { 
      icon: 'briefcaseOutline', 
      title: 'Consultoría', 
      desc: 'Modernización fiscal, tecnológica y administrativa.' 
    }
  ];

  constructor() {
    // Registro de íconos para usarlos en el HTML
    addIcons({ 
      documentTextOutline, 
      shieldCheckmarkOutline, 
      fingerPrintOutline, 
      briefcaseOutline 
    });
  }
}