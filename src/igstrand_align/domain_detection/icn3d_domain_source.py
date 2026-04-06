"""Adapter for extracting domain candidates from ICN3D numbering documents."""


class Icn3dDomainSource:
    """Expose domain candidates from a raw numbering document."""

    def iter_domains(self, numbering_document):
        raise NotImplementedError("ICN3D domain extraction is not implemented yet.")
