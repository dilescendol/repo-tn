# repo-tn

Official extension repository for `TetoNova`.

This repository is intended to host:

- the public `index.json` consumed by TetoNova
- official extension bundle manifests
- compat-import metadata and seed catalogs where needed

## Raw Index URL

```text
https://raw.githubusercontent.com/dilescendol/repo-tn/main/index.json
```

## Current Structure

```text
index.json
bundles/
compat/
```

## Current Official Wave

- `Anichin`
- `Anoboy`
- `Kuramanime`
- `Otakudesu`
- `Samehadaku`

## Notes

- `index.json` is the primary entrypoint for app-side repo refresh.
- Bundle manifests should stay lightweight and app-compatible.
- Compat seed catalogs can live alongside bundles for migration pilots such as `Anichin`.
