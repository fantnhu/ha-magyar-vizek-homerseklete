# Magyar Vizek Hőmérséklete Home Assistant Integráció

Ez az integráció a magyarországi folyók és tavak vízhőmérsékletét jeleníti meg a Home Assistant rendszerben.

## ✨ Funkciók

- Valós idejű vízhőmérséklet adatok magyar folyókról és tavakról
- Automatikus frissítés 30 percenként
- Több mérési pont támogatása
- Dinamikus ikonok a hőmérséklet függvényében
- Beállítás a felhasználói felületről

## 🛠️ Telepítés

1. Másolja a `custom_components/magyar_vizhomerseklet` mappát a Home Assistant `custom_components` könyvtárába
2. Indítsa újra a Home Assistant-ot
3. Navigáljon a Konfiguráció > Integrációk menüpontba
4. Kattintson a "+ INTEGRÁCIÓ HOZZÁADÁSA" gombra
5. Keressen rá: "Magyar Vizek Hőmérséklete"
6. Kattintson a konfigurálás gombra

## 🔄 Használat

A telepítés után az integráció két szolgáltatást hoz létre:

### Folyók
- Minden folyóhoz létrehoz egy szenzort
- A szenzor értéke az átlagos vízhőmérséklet
- Az attribútumokban megjelennek a mérési pontok és értékeik

### Tavak
- Minden tóhoz létrehoz egy szenzort
- A szenzor értéke az átlagos vízhőmérséklet
- Az attribútumokban megjelennek a mérési pontok és értékeik

### Ikonok
Az ikonok dinamikusan változnak a hőmérséklet függvényében:
- 10°C alatt: mdi:thermometer-low
- 10-15°C között: mdi:thermometer
- 15°C felett: mdi:thermometer-high

## 🤝 Közreműködés

Ha hibát találsz vagy fejlesztési javaslatod van, kérlek nyiss egy [issue-t a GitHub oldalon](https://github.com/fantnhu/ha-magyar-vizek-homerseklete/issues/)

## 📄 Licensz

Ez a projekt MIT licensz alatt áll. További információért lásd a LICENSE fájlt.

## 🔗 Hasznos linkek

- [Home Assistant közösség](https://community.home-assistant.io/)
