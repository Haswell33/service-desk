import org.semanticweb.HermiT.Reasoner;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.reasoner.NodeSet;
import org.semanticweb.owlapi.reasoner.OWLReasoner;

import java.io.*;

public class zawi {
    public static void main(String[] args) {
        System.out.println("Start");
        String prefix = "http://www.semanticweb.org/cezary/ontologies/2021/10/untitled-ontology-3";

        // tworzymy obiekty do zarządzania ontologią
        OWLOntologyManager ontologyManager = OWLManager.createOWLOntologyManager();
        OWLDataFactory owlDataFactory = ontologyManager.getOWLDataFactory();
        OWLOntology owlOntology = null;

        // 1. Załadować ontologię z pliku owl
        System.out.println("1. Wczytujemy ontologię");
        try {
            File file = new File("samoloty_protege.owl");
            owlOntology = ontologyManager.loadOntologyFromOntologyDocument(file);
        } catch (OWLOntologyCreationException e) {
            e.printStackTrace();
        }

        // 2. Wypisać na ekranie wszystkie klasy w ontologii
        System.out.println("2. Klasy:");
        assert owlOntology != null;
        for (OWLClass x : owlOntology.getClassesInSignature()) {
            System.out.println(x.getIRI().getFragment());
        }

        // 3. Wypisać na ekranie wszystkie relacje typu object-type Property w ontologii
        System.out.println("3. Właściwości obiektów:");
        for (OWLObjectProperty x : owlOntology.getObjectPropertiesInSignature()) {
            System.out.println(x.getIRI().getFragment());
        }

        // 4. Wypisać na ekranie wszystkie instancje zadanej klasy np. Samolot
        System.out.println("4. Instancje klasy 'Samolot':");
        OWLClass samolotClass = owlDataFactory.getOWLClass(IRI.create(prefix + "#Samolot"));
        for (OWLIndividual x : samolotClass.getIndividuals(owlOntology)) {
            System.out.println(x.asOWLNamedIndividual().getIRI().getFragment());
        }

        // 5. Dodać nową instancję do zadanej klasy w ontologii
        System.out.println("5. Dodajemy nową instancję 'str111111' do klasy 'Samolot'.");
        OWLIndividual jedynkiInd = owlDataFactory.getOWLNamedIndividual(IRI.create(prefix + "#str111111"));
        OWLClassAssertionAxiom classAxiom = owlDataFactory.getOWLClassAssertionAxiom(samolotClass, jedynkiInd);
        ontologyManager.applyChange(new AddAxiom(owlOntology, classAxiom));

        // 6. Utworzyć połączenie typu już istniejącej relacji object-type między nową instancją, a innym,
        // już istniejącym indywiduum.
        System.out.println("6. Dodajemy do nowo utworzonej instancji 'str111111' właściwość 'lokalizacjaSamolotu' " +
                "wskazującą na instancję 'Radom'.");
        OWLIndividual konkretneLotnisko = owlDataFactory.getOWLNamedIndividual(IRI.create(prefix + "#Radom"));
        OWLObjectProperty lokalizacjaSamolotu = owlDataFactory.getOWLObjectProperty(IRI.create(prefix + "#lokalizacjaSamolotu"));
        OWLObjectPropertyAssertionAxiom objectAxiom =
                owlDataFactory.getOWLObjectPropertyAssertionAxiom(lokalizacjaSamolotu, jedynkiInd, konkretneLotnisko);
        ontologyManager.applyChange(new AddAxiom(owlOntology, objectAxiom));

        // 7. Uruchomić mechanizm wnioskujący.
        System.out.println("7. Uruchamiamy mechanizm wnioskujący.");
        OWLReasoner owlReasoner = new Reasoner.ReasonerFactory().createReasoner(owlOntology);

        // 8. Wypisać na ekranie instancje należące do zadanej klasy z uwzględnieniem faktów wydedukowanych
        // przez mechanizm wnioskujący.
        System.out.println("8. Wywnioskowane instancje klasy 'Podejrzana_osoba':");
        OWLClass klasa_pod_osoby = owlDataFactory.getOWLClass(IRI.create(prefix + "#Podejrzana_osoba"));
        NodeSet<OWLNamedIndividual> instances = owlReasoner.getInstances(klasa_pod_osoby, true);
        for(OWLNamedIndividual instance: instances.getFlattened()){
            System.out.println(instance.getIRI().getFragment());
        }

        // 9. zapisujemy zmodyfikowaną ontologię do pliku
        System.out.println("9. Zapisujemy ontologię.");
        OutputStream outputStream = null;
        try {
            outputStream = new FileOutputStream(new File("samoloty_protege_out.owl"));
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
        try {
            ontologyManager.saveOntology(owlOntology, outputStream);
        } catch (OWLOntologyStorageException e) {
            e.printStackTrace();
        }
    }
}
