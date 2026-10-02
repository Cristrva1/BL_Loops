# Aplicaciones y acoplamientos

Cada aplicacion habla con un proveedor concreto. Estas notas no nombran personas ni
ventanas de cambio.

AtlasCRM envia cobros a NortePay.

PortalClientes envia avisos a MailRelay.

InformeTrimestral exporta a ExcelLocal.

## Relaciones

- `AtlasCRM` --depends_on--> `NortePay`
- `PortalClientes` --depends_on--> `MailRelay`
- `InformeTrimestral` --depends_on--> `ExcelLocal`
